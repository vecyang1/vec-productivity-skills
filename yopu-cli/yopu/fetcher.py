"""
HTTP Fetcher & Transport for Yopu.co score pages and API endpoints.

Features:
- Encodes internal endpoints via /z/... obfuscation (v2 protocol)
- Automatic cookie acquisition and Chrome profile auto-discovery
- Configurable egress routing (direct by default, auto-fallback to ssh:<host> or proxy)
- Decodes obfuscated responses (search via XOR 157, sheets via Brotli custom dict + permutation)
- Resilient browser fallback via ego-browser DOM extraction
"""
from __future__ import annotations

import base64
import http.cookiejar
import json
import os
import re
import shlex
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .codec import (
    encode_z,
    decode_z,
    compute_sheet_t,
    decode_search_response,
    decode_sheet_payload,
    decode_data_model,
)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

DEFAULT_CONFIG_PATHS = [
    Path.home() / ".config" / "yopu" / "egress",
    Path.home() / ".config" / "yopu-pdf" / "egress",
]

DEFAULT_COOKIE_FILE = Path.home() / ".config" / "yopu" / "cookies.json"


def safe_b64decode(data: bytes) -> bytes:
    clean = b"".join(data.split())
    pad = len(clean) % 4
    if pad:
        clean += b"=" * (4 - pad)
    return base64.b64decode(clean)


def resolve_fallback_proxy(geo: Optional[str] = None) -> Optional[str]:
    """
    Resolves residential proxy URL (SOCKS5 preferred on port 10000) via ulcs
    for transparent Cloudflare rate-limit bypass.
    """
    try:
        from ulcs.proxy import resolve_proxy_url
        url = resolve_proxy_url(geo=geo)
        if url:
            if "gw.dataimpulse.com:823" in url:
                url = url.replace("http://", "socks5h://").replace("gw.dataimpulse.com:823", "gw.dataimpulse.com:10000")
            return url
    except Exception:
        pass
    return None


def _normalize_egress_val(val: str) -> Optional[str]:
    val = val.strip()
    if not val or val.lower() == "direct":
        return None
    if val.lower().startswith("vps:"):
        return "ssh:" + val[4:].strip()
    if val.lower().startswith("proxy:"):
        geo = val[6:].strip() or None
        proxy_url = resolve_fallback_proxy(geo=geo)
        if proxy_url:
            return proxy_url
    return val


def resolve_egress(cli_egress: Optional[str] = None) -> Optional[str]:
    """
    Resolve egress spec: CLI flag > YOPU_EGRESS env > config file.
    Returns None for direct connection.
    If ~/.config/yopu/egress exists, it is authoritative (does not bleed into yopu-pdf).
    Normalizes vps:<host> -> ssh:<host> and proxy:<geo> -> residential proxy.
    """
    if cli_egress and cli_egress.strip():
        return _normalize_egress_val(cli_egress)

    env_val = os.environ.get("YOPU_EGRESS")
    if env_val and env_val.strip():
        return _normalize_egress_val(env_val)

    # Primary config: ~/.config/yopu/egress
    primary = Path.home() / ".config" / "yopu" / "egress"
    if primary.exists():
        try:
            for line in primary.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    return _normalize_egress_val(line)
            return None
        except OSError:
            pass

    # Secondary fallback ONLY if primary config does not exist
    sec = Path.home() / ".config" / "yopu-pdf" / "egress"
    if sec.exists():
        try:
            for line in sec.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    return _normalize_egress_val(line)
        except OSError:
            pass

    return None


def extract_browser_cookies() -> Dict[str, str]:
    """
    Auto-discovers and extracts Yopu login cookies from Chrome profiles.
    Prioritizes Profile 2 (Growth/Cowork), Default, Profile 1, Profile 3.
    """
    # 1. Try browser_cookie3 in current Python if available
    try:
        import browser_cookie3  # type: ignore
        chrome_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome")
        profiles = ["Profile 2", "Default", "Profile 1", "Profile 3"]
        for p in profiles:
            for sub in ["Cookies", os.path.join("Network", "Cookies")]:
                db = os.path.join(chrome_dir, p, sub)
                if os.path.exists(db):
                    try:
                        cj = browser_cookie3.chrome(cookie_file=db, domain_name="yopu.co")
                        res = {c.name: c.value for c in cj}
                        if "connect.sid" in res:
                            return res
                    except Exception:
                        pass
    except ImportError:
        pass

    # 2. Try known Python virtualenvs with browser_cookie3
    known_pythons = [
        Path.home() / ".gemini" / "antigravity" / "skills" / "gemini-webapi" / ".venv" / "bin" / "python",
        Path.home() / ".venv" / "bin" / "python",
        Path.home() / "venv" / "bin" / "python",
    ]
    sub_script = """
import browser_cookie3, os, json
chrome_dir = os.path.expanduser('~/Library/Application Support/Google/Chrome')
profiles = ['Profile 2', 'Default', 'Profile 1', 'Profile 3']
found = {}
for p in profiles:
    for sub in ['Cookies', os.path.join('Network', 'Cookies')]:
        db = os.path.join(chrome_dir, p, sub)
        if os.path.exists(db):
            try:
                cj = browser_cookie3.chrome(cookie_file=db, domain_name='yopu.co')
                m = {c.name: c.value for c in cj}
                if 'connect.sid' in m:
                    found = m
                    break
            except Exception:
                pass
    if found:
        break
print(json.dumps(found))
"""
    for py in known_pythons:
        if py.exists():
            try:
                proc = subprocess.run([str(py), "-c", sub_script], capture_output=True, text=True, timeout=5)
                if proc.returncode == 0 and proc.stdout.strip():
                    data = json.loads(proc.stdout.strip())
                    if isinstance(data, dict) and data.get("connect.sid"):
                        return data
            except Exception:
                pass

    return {}


def get_1password_yopu_credentials() -> Dict[str, str]:
    """
    Queries 1Password CLI (op) or op_unattended for Yopu / 有谱么 credentials or session cookies.
    Searches known exact titles, and searches item lists if not found directly.
    """
    candidate_scripts = [
        Path.home() / ".agents" / "skills" / "1password" / "scripts" / "op_unattended.py",
        Path.home() / ".gemini" / "antigravity" / "skills" / "1password" / "scripts" / "op_unattended.py",
        Path.home() / ".gemini" / "config" / "skills" / "1password" / "scripts" / "op_unattended.py",
    ]
    unattended_script = next((p for p in candidate_scripts if p.exists()), None)

    known_titles = [
        os.environ.get("YOPU_1PASSWORD_TITLE", ""),
        "yopu",
        "yopu.co",
        "youpu",
        "有谱么",
    ]
    known_titles = [t for t in known_titles if t]

    def _parse_item_data(data: dict) -> Dict[str, str]:
        cookies: Dict[str, str] = {}
        for f in data.get("fields", []):
            label = f.get("label", "").lower()
            val = f.get("value", "")
            if not val:
                continue
            if "connect.sid" in label or label in ("cookie", "sid"):
                cookies["connect.sid"] = val
            elif label == "c":
                cookies["c"] = val
        notes = data.get("notesPlain", "")
        if notes and "connect.sid" in notes:
            for part in notes.replace("\\n", ";").replace("\n", ";").split(";"):
                if "=" in part:
                    k, v = part.strip().split("=", 1)
                    if k.strip() in ("connect.sid", "c") and k.strip() not in cookies:
                        cookies[k.strip()] = v.strip()
        return cookies

    # 1. Try known titles
    for t in known_titles:
        cmd = [sys.executable, str(unattended_script), "--", "op", "item", "get", t, "--format=json"] if unattended_script else ["op", "item", "get", t, "--format=json"]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
            if proc.returncode == 0 and proc.stdout.strip():
                data = json.loads(proc.stdout)
                cookies = _parse_item_data(data)
                if "connect.sid" in cookies:
                    return cookies
        except Exception:
            pass

    # 2. Search item list if exact titles didn't hit
    cmd_list = [sys.executable, str(unattended_script), "--", "op", "item", "list", "--format=json"] if unattended_script else ["op", "item", "list", "--format=json"]
    try:
        proc = subprocess.run(cmd_list, capture_output=True, text=True, timeout=10)
        if proc.returncode == 0 and proc.stdout.strip():
            items = json.loads(proc.stdout)
            for it in items:
                title = it.get("title", "").lower()
                urls = [u.get("href", "").lower() for u in it.get("urls", [])]
                if any(k in title or any(k in u for u in urls) for k in ("yopu", "youpu", "有谱")):
                    item_id = it.get("id")
                    cmd_get = [sys.executable, str(unattended_script), "--", "op", "item", "get", item_id, "--format=json"] if unattended_script else ["op", "item", "get", item_id, "--format=json"]
                    proc2 = subprocess.run(cmd_get, capture_output=True, text=True, timeout=8)
                    if proc2.returncode == 0 and proc2.stdout.strip():
                        data = json.loads(proc2.stdout)
                        cookies = _parse_item_data(data)
                        if "connect.sid" in cookies:
                            return cookies
    except Exception:
        pass

    return {}


def load_yopu_cookies(auto_extract: bool = True, force_refresh: bool = False) -> Dict[str, str]:
    """
    Loads Yopu session cookies with automated fallback and persistence.
    1. YOPU_COOKIE environment variable
    2. ~/.config/yopu/cookies.json (unless force_refresh is True)
    3. Chrome profile auto-extraction (Profile 2 / Default / Profile 1)
    4. 1Password credential lookup
    """
    # 1. Environment variable
    env_c = os.environ.get("YOPU_COOKIE")
    if env_c and env_c.strip():
        parts = [p.strip() for p in env_c.split(";") if "=" in p]
        return dict(p.split("=", 1) for p in parts)

    # 2. Config file
    if not force_refresh and DEFAULT_COOKIE_FILE.exists():
        try:
            data = json.loads(DEFAULT_COOKIE_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("connect.sid"):
                return data
        except Exception:
            pass

    # 3. Auto-extract from Chrome
    if auto_extract:
        cookies = extract_browser_cookies()
        if cookies and cookies.get("connect.sid"):
            try:
                DEFAULT_COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
                DEFAULT_COOKIE_FILE.write_text(json.dumps(cookies, indent=2), encoding="utf-8")
                DEFAULT_COOKIE_FILE.chmod(0o600)
            except Exception:
                pass
            return cookies

    # 4. Check 1Password
    op_cookies = get_1password_yopu_credentials()
    if op_cookies and op_cookies.get("connect.sid"):
        try:
            DEFAULT_COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
            DEFAULT_COOKIE_FILE.write_text(json.dumps(op_cookies, indent=2), encoding="utf-8")
            DEFAULT_COOKIE_FILE.chmod(0o600)
        except Exception:
            pass
        return op_cookies

    return {}


def extract_score_id(input_str: str) -> str:
    """
    Extracts the Yopu score ID from a URL, path, or raw ID string.
    Example: 'https://yopu.co/view/aPenOOpb' -> 'aPenOOpb'
    """
    input_str = input_str.strip()
    match = re.search(r"yopu\.co/(?:view|sheet)/([a-zA-Z0-9_-]+)", input_str)
    if match:
        return match.group(1)
    clean_id = re.sub(r"^https?://[^/]+/", "", input_str).strip("/").split("?")[0]
    if re.match(r"^[a-zA-Z0-9_-]+$", clean_id):
        return clean_id
    return input_str


def build_score_url(score_id_or_url: str) -> str:
    """Build canonical Yopu URL from ID or URL."""
    score_id = extract_score_id(score_id_or_url)
    return f"https://yopu.co/view/{score_id}"


class YopuClient:
    """
    Unified client for communicating with Yopu.co.
    Handles authenticated session cookies, /z/ obfuscation, and egress routing.
    """

    def __init__(self, egress: Optional[str] = None, timeout: int = 15, cookies: Optional[Dict[str, str]] = None):
        self.egress = resolve_egress(egress)
        self.timeout = timeout
        self.cookies = cookies if cookies is not None else load_yopu_cookies()
        self.jar = http.cookiejar.CookieJar()
        self._populate_cookie_jar()
        self._opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

    def _populate_cookie_jar(self) -> None:
        """Populate cookie jar with initial authenticated cookies."""
        for name, val in self.cookies.items():
            for domain in ("yopu.co", ".yopu.co"):
                ck = http.cookiejar.Cookie(
                    version=0,
                    name=name,
                    value=val,
                    port=None,
                    port_specified=False,
                    domain=domain,
                    domain_specified=True,
                    domain_initial_dot=domain.startswith("."),
                    path="/",
                    path_specified=True,
                    secure=True,
                    expires=None,
                    discard=False,
                    comment=None,
                    comment_url=None,
                    rest={"HttpOnly": None},
                )
                self.jar.set_cookie(ck)

    @property
    def cookie_header(self) -> str:
        """Formatted Cookie request header value."""
        return "; ".join(f"{k}={v}" for k, v in self.cookies.items())

    def _is_empty_404(self, exc: urllib.error.HTTPError) -> bool:
        """Check if HTTPError is the specific IP-ban symptom: 404 with 0 bytes body."""
        if exc.code != 404:
            return False
        try:
            body = exc.read()
            return len(body) == 0
        except Exception:
            return False

    def _parse_http_dump(self, raw: bytes) -> Tuple[int, Dict[str, str], bytes]:
        """Parse curl -D dump into status, headers, and body."""
        parts = raw.split(b"\r\n\r\n")
        hdr_idx = 0
        for i, p in enumerate(parts):
            if p[:5] == b"HTTP/":
                hdr_idx = i
        head = parts[hdr_idx]
        body = b"\r\n\r\n".join(parts[hdr_idx + 1:])
        lines = head.split(b"\r\n")
        status = int(lines[0].split()[1]) if lines and lines[0][:5] == b"HTTP/" else 0
        resp_headers = {}
        for line in lines[1:]:
            if b":" in line:
                k, v = line.split(b":", 1)
                resp_headers[k.decode("latin1").strip().lower()] = v.decode("latin1").strip()
        return status, resp_headers, body

    def fetch_url(self, url: str, referer: str = "https://yopu.co/", extra_headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None) -> bytes:
        """
        Fetch a URL. Routes via SSH egress if configured; otherwise direct.
        Falls back to egress if direct receives empty 404 (IP ban).
        """
        req_timeout = timeout if timeout is not None else self.timeout
        headers = {
            "User-Agent": USER_AGENT,
            "Referer": referer,
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        if self.cookie_header:
            headers["Cookie"] = self.cookie_header
        if extra_headers:
            headers.update(extra_headers)

        # 1. If explicit SSH egress configured
        if self.egress and self.egress.lower().startswith("ssh:"):
            host = self.egress[4:].strip()
            fallback_needed = False
            fallback_reason = ""
            try:
                cookie_arg = f"-H {shlex.quote(f'Cookie: {self.cookie_header}')}" if self.cookie_header else ""
                cmd = f"curl -s --no-keepalive --compressed -D - -H {shlex.quote(f'User-Agent: {USER_AGENT}')} -H {shlex.quote(f'Referer: {referer}')} -H 'Accept: */*' {cookie_arg} {shlex.quote(url)} | base64"
                proc = subprocess.run(
                    ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", host, cmd],
                    capture_output=True, timeout=req_timeout
                )
                if proc.returncode == 0 and proc.stdout:
                    raw = safe_b64decode(proc.stdout)
                    status, _, body = self._parse_http_dump(raw)
                    if status == 200:
                        return body
                    fallback_needed = True
                    fallback_reason = f"returned HTTP {status}"
                else:
                    fallback_needed = True
                    err_msg = proc.stderr.decode("utf-8", errors="replace").strip() if proc.stderr else f"exit code {proc.returncode}"
                    fallback_reason = f"ssh failed ({err_msg})"
            except Exception as e:
                fallback_needed = True
                fallback_reason = str(e)

            if fallback_needed:
                import sys
                print(f"⚠️ [yopu-cli] Egress {host} failed ({fallback_reason}) for {url}, falling back to direct...", file=sys.stderr)

        # 2. If explicit HTTP/SOCKS proxy egress configured
        if self.egress and (self.egress.startswith("http") or self.egress.startswith("socks")):
            try:
                handler = urllib.request.ProxyHandler({"http": self.egress, "https": self.egress})
                opener = urllib.request.build_opener(handler, urllib.request.HTTPCookieProcessor(self.jar))
                req = urllib.request.Request(url, headers=headers)
                with opener.open(req, timeout=req_timeout) as resp:
                    return resp.read()
            except Exception as e:
                import sys
                print(f"⚠️ [yopu-cli] Proxy egress failed ({e}), falling back to direct...", file=sys.stderr)

        # 3. Direct fetch
        req = urllib.request.Request(url, headers=headers)
        try:
            with self._opener.open(req, timeout=req_timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if self._is_empty_404(e):
                try:
                    return self._fetch_via_proxy(url, referer=referer)
                except Exception:
                    pass
                raise ConnectionError(
                    f"Yopu.co IP rate-limit block detected (empty HTTP 404 for {url}). "
                    f"Configure an egress via --egress 'ssh:<host>' or YOPU_EGRESS env."
                )
            raise ConnectionError(f"HTTP {e.code} error connecting to Yopu ({url}): {e.reason}")
        except (urllib.error.URLError, ConnectionError):
            try:
                return self._fetch_via_proxy(url, referer=referer)
            except Exception:
                raise

    def _fetch_via_proxy(self, url: str, referer: str = "https://yopu.co/") -> bytes:
        """Fetch URL via fallback residential proxy."""
        proxy = resolve_fallback_proxy()
        if not proxy:
            raise ConnectionError("No fallback proxy available to bypass block.")

        # 1. Try curl_cffi with chrome124
        try:
            from curl_cffi import requests
            s = requests.Session(impersonate="chrome124")
            proxies = {"http": proxy, "https": proxy}
            headers = {"Referer": referer, "Accept": "*/*", "User-Agent": USER_AGENT}
            sid = self.cookies.get("connect.sid")
            if sid:
                headers["Cookie"] = f"connect.sid={sid}"
            r = s.get(url, headers=headers, proxies=proxies, timeout=self.timeout)
            if r.status_code == 200 and r.content:
                return r.content
        except Exception:
            pass

        # 2. Try curl CLI subprocess
        cmd = [
            "curl", "-s", "--compressed", "-m", str(self.timeout),
            "-x", proxy,
            "-H", f"User-Agent: {USER_AGENT}",
            "-H", f"Referer: {referer}",
        ]
        sid = self.cookies.get("connect.sid")
        if sid:
            cmd.extend(["-H", f"Cookie: connect.sid={sid}"])
        cmd.append(url)
        proc = subprocess.run(cmd, capture_output=True, timeout=self.timeout + 5)
        if proc.returncode == 0 and proc.stdout:
            return proc.stdout
        raise ConnectionError(f"Failed to fetch {url} via fallback proxy.")

    def _fetch_session_via_proxy(self, init_url: str, target_z_path: str, referer: str) -> bytes:
        """Initializes session and fetches target path via fallback residential proxy."""
        proxy = resolve_fallback_proxy()
        if not proxy:
            raise ConnectionError("No fallback proxy available to bypass block.")

        target_url = urllib.parse.urljoin("https://yopu.co", target_z_path)
        sid = self.cookies.get("connect.sid")

        # 1. Try curl_cffi with session cookie continuity
        try:
            from curl_cffi import requests
            s = requests.Session(impersonate="chrome124")
            proxies = {"http": proxy, "https": proxy}
            if sid:
                s.cookies.set("connect.sid", sid, domain="yopu.co")
            s.get(init_url, proxies=proxies, timeout=max(self.timeout, 25))

            req_headers = {"Referer": referer, "Accept": "*/*", "User-Agent": USER_AGENT}
            r2 = s.get(target_url, headers=req_headers, proxies=proxies, timeout=max(self.timeout, 25))
            if r2.status_code == 200 and r2.content and len(r2.content) > 100:
                return r2.content
        except Exception:
            pass

        # 2. Subprocess curl with cookie jar fallback
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as f:
            jar = f.name
        try:
            doc_cmd = [
                "curl", "-s", "-m", str(max(self.timeout, 25)),
                "-x", proxy, "-c", jar,
                "-H", f"User-Agent: {USER_AGENT}",
            ]
            if sid:
                doc_cmd.extend(["-H", f"Cookie: connect.sid={sid}"])
            doc_cmd.append(init_url)
            subprocess.run(doc_cmd, capture_output=True, timeout=self.timeout + 10)

            target_cmd = [
                "curl", "-s", "--compressed", "-m", str(max(self.timeout, 25)),
                "-x", proxy, "-b", jar,
                "-H", f"User-Agent: {USER_AGENT}",
                "-H", f"Referer: {referer}",
                "-H", "Accept: */*",
            ]
            if sid:
                target_cmd.extend(["-H", f"Cookie: connect.sid={sid}"])
            target_cmd.append(target_url)
            p = subprocess.run(target_cmd, capture_output=True, timeout=self.timeout + 10)
            if p.returncode == 0 and p.stdout and len(p.stdout) > 100:
                return p.stdout
        finally:
            if os.path.exists(jar):
                try:
                    os.remove(jar)
                except OSError:
                    pass

        raise ConnectionError(f"Failed to fetch session {target_z_path} via fallback proxy.")

    def fetch_with_session(self, init_url: str, target_z_path: str, referer: str) -> bytes:
        """
        Initializes session by visiting init_url (to obtain or refresh cookies),
        then fetches target_z_path using the same egress and cookie jar.
        """
        headers = {
            "User-Agent": USER_AGENT,
            "Referer": referer,
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        if self.cookie_header:
            headers["Cookie"] = self.cookie_header

        # 1. SSH egress (single atomic roundtrip)
        if self.egress and self.egress.lower().startswith("ssh:"):
            host = self.egress[4:].strip()
            target_url = urllib.parse.urljoin("https://yopu.co", target_z_path)
            fallback_needed = False
            fallback_reason = ""
            try:
                cookie_arg = f"-H {shlex.quote(f'Cookie: {self.cookie_header}')}" if self.cookie_header else ""
                cmd = f"""
J=$(mktemp)
curl -s --no-keepalive -c "$J" {cookie_arg} {shlex.quote(init_url)} > /dev/null
curl -s --no-keepalive --compressed -D - -b "$J" {cookie_arg} -H {shlex.quote(f'User-Agent: {USER_AGENT}')} -H {shlex.quote(f'Referer: {referer}')} -H 'Accept: */*' {shlex.quote(target_url)} | base64
rm -f "$J"
"""
                proc = subprocess.run(
                    ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", host, cmd],
                    capture_output=True, timeout=15
                )
                if proc.returncode == 0 and proc.stdout:
                    raw = safe_b64decode(proc.stdout)
                    status, _, body = self._parse_http_dump(raw)
                    if status == 200:
                        return body
                    fallback_needed = True
                    fallback_reason = f"returned HTTP {status}"
                else:
                    fallback_needed = True
                    err_msg = proc.stderr.decode("utf-8", errors="replace").strip() if proc.stderr else f"exit code {proc.returncode}"
                    fallback_reason = f"ssh failed ({err_msg})"
            except Exception as e:
                fallback_needed = True
                fallback_reason = str(e)

            if fallback_needed:
                import sys
                print(f"⚠️ [yopu-cli] Egress {host} failed ({fallback_reason}) for {target_z_path}, falling back to direct...", file=sys.stderr)

        # 2. Proxy egress
        if self.egress and (self.egress.startswith("http") or self.egress.startswith("socks")):
            try:
                handler = urllib.request.ProxyHandler({"http": self.egress, "https": self.egress})
                opener = urllib.request.build_opener(handler, urllib.request.HTTPCookieProcessor(self.jar))
                opener.open(urllib.request.Request(init_url, headers=headers), timeout=self.timeout)
                target_url = urllib.parse.urljoin("https://yopu.co", target_z_path)
                with opener.open(urllib.request.Request(target_url, headers=headers), timeout=self.timeout) as resp:
                    return resp.read()
            except Exception as e:
                import sys
                print(f"⚠️ [yopu-cli] Proxy egress failed ({e}), falling back to direct...", file=sys.stderr)

        # 3. Direct
        try:
            self._opener.open(urllib.request.Request(init_url, headers=headers), timeout=self.timeout)
            target_url = urllib.parse.urljoin("https://yopu.co", target_z_path)
            with self._opener.open(urllib.request.Request(target_url, headers=headers), timeout=self.timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if self._is_empty_404(e):
                try:
                    return self._fetch_session_via_proxy(init_url, target_z_path, referer)
                except Exception:
                    pass
                raise ConnectionError(
                    f"Yopu.co IP rate-limit block detected (empty HTTP 404). "
                    f"Configure an egress via --egress 'ssh:<host>' or YOPU_EGRESS env."
                )
            raise ConnectionError(f"HTTP {e.code} error from Yopu: {e.reason}")
        except (urllib.error.URLError, ConnectionError):
            try:
                return self._fetch_session_via_proxy(init_url, target_z_path, referer)
            except Exception:
                raise

    def search_scores(self, query: str, page: int = 0, instrument: str = "guitar") -> Dict[str, Any]:
        """Search Yopu.co for lead sheets matching query (API v2)."""
        params = {
            "q": query.strip(),
            "page": page,
            "instrument": instrument,
            "v": 2,
        }
        api_path = "/api/search/sheets?" + urllib.parse.urlencode(params)
        z_path = encode_z(api_path)
        raw_bytes = self.fetch_with_session(
            init_url="https://yopu.co/explore",
            target_z_path=z_path,
            referer="https://yopu.co/explore"
        )
        data = decode_search_response(raw_bytes)

        results = []
        for item in data.get("results", []):
            entry_type = item.get("entryType")
            if entry_type == "song" and item.get("sheets"):
                for sheet in item["sheets"]:
                    owner = sheet.get("owner", {})
                    author_name = owner.get("displayName") if isinstance(owner, dict) else str(owner or "")
                    results.append({
                        "id": sheet.get("id"),
                        "title": item.get("title", ""),
                        "artist": item.get("artist", ""),
                        "key": sheet.get("key", ""),
                        "capo": sheet.get("capo", 0),
                        "author": author_name,
                        "verified": bool(sheet.get("verified", False)),
                        "views": sheet.get("guitarUniqViews") or sheet.get("uniqViews", 0),
                        "rating": round(sheet.get("rating", 0), 1),
                        "tags": sheet.get("tags", []),
                        "url": f"https://yopu.co/view/{sheet.get('id')}"
                    })
            else:
                sheet_id = item.get("_id") or item.get("id")
                if not sheet_id:
                    continue
                owner = item.get("owner") or item.get("author", {})
                author_name = owner.get("displayName") or owner.get("name") if isinstance(owner, dict) else str(owner or "")
                results.append({
                    "id": sheet_id,
                    "title": item.get("title", ""),
                    "artist": item.get("artist", ""),
                    "key": item.get("key", ""),
                    "capo": item.get("capo", 0),
                    "author": author_name,
                    "verified": bool(item.get("verified", False)),
                    "views": item.get("uniqViews") or item.get("views", 0),
                    "rating": round(item.get("rating", 0), 1),
                    "tags": item.get("tags", []),
                    "url": f"https://yopu.co/view/{sheet_id}"
                })

        return {
            "query": query,
            "total_count": data.get("totalResultNum", len(results)),
            "results": results
        }

    def fetch_sheet_data_via_browser(self, score_id: str) -> Dict[str, Any]:
        """
        Fallback DOM extraction using ego-browser.
        Used when edge TLS filters or IP challenges block direct /z/ HTTP calls.
        """
        cfg_path = Path.home() / ".config" / "yopu" / "cookies.json"
        script = f'''
const task = await taskSpace("yp browser fallback");
const page = task.page("p1");

const fs = await import("node:fs");
const cfgPath = "{cfg_path}";
if (fs.existsSync(cfgPath)) {{
  const raw = JSON.parse(fs.readFileSync(cfgPath, "utf-8"));
  const cookies = Object.entries(raw).map(([name, value]) => ({{
    name, value, domain: "yopu.co", path: "/"
  }}));
  await page.cdp("Network.setCookies", {{ cookies }});
}}

await page.goto("https://yopu.co/view/{score_id}");
await page.waitForTimeout(2500);

const extracted = await page.evaluate(() => {{
  const titleEl = document.querySelector('h1, .title, title');
  const rawTitle = titleEl ? titleEl.textContent.trim() : '';
  const svgs = Array.from(document.querySelectorAll('#nier-scroll-view svg'));
  const allChords = [];
  const seenChords = new Set();

  const measures = svgs.map((svg, idx) => {{
    const texts = Array.from(svg.querySelectorAll('text')).map(t => ({{
      text: t.textContent.trim(),
      x: parseFloat(t.getAttribute('x') || 0),
      y: parseFloat(t.getAttribute('y') || 0),
    }})).filter(t => t.text.length > 0);
    
    const chords = texts.filter(t => t.y < 50 && !['', '', '', ''].includes(t.text) && !/^[0-9]$/.test(t.text));
    for (const c of chords) {{
      if (!seenChords.has(c.text)) {{
        seenChords.add(c.text);
        allChords.push(c.text);
      }}
    }}
    const section = texts.find(t => t.y > 50 && t.y < 120 && ['前奏', '主歌', '副歌', '间奏', '尾奏', '尾声', '转调', '高潮', '过渡', 'Intro', 'Verse', 'Chorus', 'Bridge', 'Outro'].some(k => t.text.includes(k)));
    const lyrics = texts.filter(t => t.y > 230).sort((a, b) => a.x - b.x).map(l => l.text).join('');
    
    return {{
      measure: idx + 1,
      chords: chords.map(c => c.text),
      section: section ? section.text : null,
      lyrics
    }};
  }});
  return {{ rawTitle, allChords, measures }};
}});

console.log('EXTRACTED_JSON_START' + JSON.stringify(extracted) + 'EXTRACTED_JSON_END');
await task.finish({{ keep: [] }});
'''
        proc = subprocess.run(["ego-browser", "nodejs"], input=script, text=True, capture_output=True, timeout=30)
        combined = proc.stdout + "\n" + proc.stderr
        if "EXTRACTED_JSON_START" in combined:
            raw_json = combined.split("EXTRACTED_JSON_START", 1)[1].split("EXTRACTED_JSON_END", 1)[0]
            data = json.loads(raw_json)
            raw_title = data.get("rawTitle", "")
            title_clean = re.sub(r"\s*(?:吉他和弦谱|吉他谱|和弦谱|尤克里里谱|尤克里里和弦谱|钢琴谱|弹唱谱)\s*$", "", raw_title)
            parts = title_clean.split("-", 1)
            title = parts[0].strip() if parts else raw_title
            artist = parts[1].strip() if len(parts) > 1 else ""

            lyrics_lines = []
            for m in data.get("measures", []):
                if m.get("lyrics"):
                    lyrics_lines.append(m["lyrics"])

            return {
                "id": score_id,
                "title": title,
                "artist": artist,
                "chords": data.get("allChords", []),
                "lyrics": "\n".join(lyrics_lines),
                "browser_measures": data.get("measures", []),
                "source": "ego-browser",
            }
        raise RuntimeError(f"ego-browser extraction failed: {proc.stderr[:200]}")

    def _fetch_sheet_data_direct(self, score_id: str) -> Dict[str, Any]:
        """
        Fetches score HTML, derives session-bound token t, and fetches sheet payload
        via direct connection or configured SSH/proxy egress.
        """
        view_url = f"https://yopu.co/view/{score_id}"

        # When no explicit egress is pinned, probe direct connection cleanly without falling back to proxy mid-flight
        if not self.egress:
            headers = {
                "User-Agent": USER_AGENT,
                "Referer": "https://yopu.co/",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }
            if self.cookie_header:
                headers["Cookie"] = self.cookie_header
            req = urllib.request.Request(view_url, headers=headers)
            with self._opener.open(req, timeout=3) as resp:
                raw_html = resp.read().decode("utf-8", errors="replace")
        else:
            raw_html = self.fetch_url(view_url, referer="https://yopu.co/", timeout=self.timeout).decode("utf-8", errors="replace")
        token_t = None
        m = re.search(r'data-model="([^"]+)"', raw_html)
        if m:
            model_data = decode_data_model(m.group(1))
            st = model_data.get("st")
            if st:
                token_t = compute_sheet_t(st)

        api_path = f"/api/sheet?code={score_id}&instrument=guitar&screen=2&v=2"
        if token_t:
            api_path += f"&t={token_t}"
        z_path = encode_z(api_path)

        raw_bytes = self.fetch_with_session(
            init_url=view_url,
            target_z_path=z_path,
            referer=view_url
        )
        sheet_meta = decode_sheet_payload(raw_bytes)

        v4_url = sheet_meta.get("scoreUrlV4")
        if v4_url:
            try:
                cdn_req = urllib.request.Request(v4_url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(cdn_req, timeout=self.timeout) as resp:
                    v4_raw = resp.read()
                sheet_meta["v4_data"] = decode_sheet_payload(v4_raw)
            except Exception:
                pass

        return sheet_meta

    def _fetch_sheet_data_via_proxy(self, score_id: str) -> Dict[str, Any]:
        """
        Fetches score HTML, derives session-bound token t, and fetches sheet payload atomically
        via residential proxy and curl_cffi.
        """
        proxy = resolve_fallback_proxy()
        if not proxy:
            raise ConnectionError("No fallback proxy available to bypass block.")

        view_url = f"https://yopu.co/view/{score_id}"
        sid = self.cookies.get("connect.sid")
        proxies = {"http": proxy, "https": proxy}

        # 1. Try curl_cffi with session continuity
        try:
            from curl_cffi import requests
            s = requests.Session(impersonate="chrome124")
            if sid:
                s.cookies.set("connect.sid", sid, domain="yopu.co")

            init_resp = s.get(view_url, proxies=proxies, timeout=max(self.timeout, 25))
            if init_resp.status_code == 200 and init_resp.text:
                token_t = None
                m = re.search(r'data-model="([^"]+)"', init_resp.text)
                if m:
                    model_data = decode_data_model(m.group(1))
                    st = model_data.get("st")
                    if st:
                        token_t = compute_sheet_t(st)

                api_path = f"/api/sheet?code={score_id}&instrument=guitar&screen=2&v=2"
                if token_t:
                    api_path += f"&t={token_t}"
                z_path = encode_z(api_path)
                target_url = urllib.parse.urljoin("https://yopu.co", z_path)

                req_headers = {"Referer": view_url, "Accept": "*/*", "User-Agent": USER_AGENT}
                r2 = s.get(target_url, headers=req_headers, proxies=proxies, timeout=max(self.timeout, 25))
                if r2.status_code == 200 and r2.content:
                    sheet_meta = decode_sheet_payload(r2.content)
                    v4_url = sheet_meta.get("scoreUrlV4")
                    if v4_url:
                        try:
                            rv4 = s.get(v4_url, timeout=self.timeout)
                            if rv4.status_code == 200:
                                sheet_meta["v4_data"] = decode_sheet_payload(rv4.content)
                        except Exception:
                            pass
                    return sheet_meta
        except Exception:
            pass

        # 2. Try curl CLI subprocess fallback with cookie jar
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as f:
            jar = f.name
        try:
            doc_cmd = [
                "curl", "-s", "--compressed", "-m", str(max(self.timeout, 25)),
                "-x", proxy, "-c", jar,
                "-H", f"User-Agent: {USER_AGENT}",
                "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            ]
            if sid:
                doc_cmd.extend(["-H", f"Cookie: connect.sid={sid}"])
            doc_cmd.append(view_url)
            p1 = subprocess.run(doc_cmd, capture_output=True, timeout=self.timeout + 10)
            if p1.returncode == 0 and p1.stdout:
                html = p1.stdout.decode("utf-8", errors="replace")
                token_t = None
                m = re.search(r'data-model="([^"]+)"', html)
                if m:
                    model_data = decode_data_model(m.group(1))
                    st = model_data.get("st")
                    if st:
                        token_t = compute_sheet_t(st)

                api_path = f"/api/sheet?code={score_id}&instrument=guitar&screen=2&v=2"
                if token_t:
                    api_path += f"&t={token_t}"
                z_path = encode_z(api_path)
                target_url = urllib.parse.urljoin("https://yopu.co", z_path)

                target_cmd = [
                    "curl", "-s", "--compressed", "-m", str(max(self.timeout, 25)),
                    "-x", proxy, "-b", jar,
                    "-H", f"User-Agent: {USER_AGENT}",
                    "-H", f"Referer: {view_url}",
                    "-H", "Accept: */*",
                ]
                if sid:
                    target_cmd.extend(["-H", f"Cookie: connect.sid={sid}"])
                target_cmd.append(target_url)
                p2 = subprocess.run(target_cmd, capture_output=True, timeout=self.timeout + 10)
                if p2.returncode == 0 and p2.stdout:
                    sheet_meta = decode_sheet_payload(p2.stdout)
                    v4_url = sheet_meta.get("scoreUrlV4")
                    if v4_url:
                        try:
                            cdn_req = urllib.request.Request(v4_url, headers={"User-Agent": USER_AGENT})
                            with urllib.request.urlopen(cdn_req, timeout=self.timeout) as resp:
                                sheet_meta["v4_data"] = decode_sheet_payload(resp.read())
                        except Exception:
                            pass
                    return sheet_meta
        finally:
            if os.path.exists(jar):
                try:
                    os.remove(jar)
                except OSError:
                    pass

        raise ConnectionError(f"Failed to fetch sheet data for {score_id} via proxy.")

    def fetch_sheet_data(self, score_id_or_url: str) -> Dict[str, Any]:
        """
        Fetch full structured sheet data for a score ID from Yopu.co.
        Fetches /api/sheet?code=<id>&instrument=guitar&screen=2&t=<t>&v=2.
        Falls back to proxy or ego-browser E2E extraction on edge restrictions.
        """
        score_id = extract_score_id(score_id_or_url)
        try:
            return self._fetch_sheet_data_direct(score_id)
        except Exception as direct_exc:
            try:
                return self._fetch_sheet_data_via_proxy(score_id)
            except Exception as proxy_exc:
                try:
                    return self.fetch_sheet_data_via_browser(score_id)
                except Exception:
                    raise proxy_exc or direct_exc


# Convenience module-level functions
def search_yopu_scores(query: str, page: int = 0, instrument: str = "guitar", egress: Optional[str] = None) -> Dict[str, Any]:
    client = YopuClient(egress=egress)
    return client.search_scores(query=query, page=page, instrument=instrument)


def fetch_score_data(score_id_or_url: str, egress: Optional[str] = None) -> Dict[str, Any]:
    client = YopuClient(egress=egress)
    return client.fetch_sheet_data(score_id_or_url)


def fetch_score_html(score_id_or_url: str, timeout: int = 15) -> Tuple[str, str]:
    """Compatibility wrapper for HTML parsing."""
    url = build_score_url(score_id_or_url)
    client = YopuClient(timeout=timeout)
    raw_html = client.fetch_url(url, referer="https://yopu.co/").decode("utf-8", errors="replace")
    return raw_html, url
