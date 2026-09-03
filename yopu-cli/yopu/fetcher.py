"""
HTTP Fetcher & Transport for Yopu.co score pages and API endpoints.

Features:
- Encodes internal endpoints via /z/... obfuscation
- Automatic cookie acquisition (c=... token) from /explore or /view/<id>
- Configurable egress routing (direct by default, auto-fallback to ssh:<host> or proxy)
- Decodes obfuscated responses (search via XOR 157, sheets via V+q7)
"""
from __future__ import annotations

import base64
import http.cookiejar
import json
import os
import re
import shlex
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .codec import encode_z, decode_search_response, decode_sheet_payload

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

DEFAULT_CONFIG_PATHS = [
    Path.home() / ".config" / "yopu" / "egress",
    Path.home() / ".config" / "yopu-pdf" / "egress",
]


def resolve_egress(cli_egress: Optional[str] = None) -> Optional[str]:
    """
    Resolve egress spec: CLI flag > YOPU_EGRESS / YOPU_PDF_EGRESS env > config file.
    Returns None for direct connection.
    """
    if cli_egress and cli_egress.strip():
        return cli_egress.strip()

    env_val = os.environ.get("YOPU_EGRESS") or os.environ.get("YOPU_PDF_EGRESS")
    if env_val and env_val.strip():
        return env_val.strip()

    for p in DEFAULT_CONFIG_PATHS:
        if p.exists():
            try:
                for line in p.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        return line
            except OSError:
                pass
    return None


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
    Handles session cookies, /z/ obfuscation, and egress routing.
    """

    def __init__(self, egress: Optional[str] = None, timeout: int = 15):
        self.egress = resolve_egress(egress)
        self.timeout = timeout
        self.jar = http.cookiejar.CookieJar()
        self._opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

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

    def fetch_url(self, url: str, referer: str = "https://yopu.co/", extra_headers: Optional[Dict[str, str]] = None) -> bytes:
        """
        Fetch a URL. Routes via SSH egress if configured; otherwise direct.
        Falls back to egress if direct receives empty 404 (IP ban).
        """
        headers = {
            "User-Agent": USER_AGENT,
            "Referer": referer,
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        if extra_headers:
            headers.update(extra_headers)

        # 1. If explicit SSH egress configured
        if self.egress and self.egress.lower().startswith("ssh:"):
            host = self.egress[4:].strip()
            cmd = f"curl -s --no-keepalive --compressed -D - -H {shlex.quote(f'User-Agent: {USER_AGENT}')} -H {shlex.quote(f'Referer: {referer}')} -H 'Accept: */*' {shlex.quote(url)} | base64"
            proc = subprocess.run(
                ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", host, cmd],
                capture_output=True, timeout=60
            )
            if proc.returncode != 0 and not proc.stdout:
                raise RuntimeError(f"SSH relay to {host} failed: {proc.stderr.decode('utf-8', 'replace')}")
            raw = base64.b64decode(proc.stdout)
            status, _, body = self._parse_http_dump(raw)
            if status != 200:
                raise ConnectionError(f"Egress {host} returned HTTP {status} for {url}")
            return body

        # 2. If explicit HTTP/SOCKS proxy egress configured
        if self.egress and (self.egress.startswith("http") or self.egress.startswith("socks")):
            handler = urllib.request.ProxyHandler({"http": self.egress, "https": self.egress})
            opener = urllib.request.build_opener(handler, urllib.request.HTTPCookieProcessor(self.jar))
            req = urllib.request.Request(url, headers=headers)
            with opener.open(req, timeout=self.timeout) as resp:
                return resp.read()

        # 3. Direct fetch
        req = urllib.request.Request(url, headers=headers)
        try:
            with self._opener.open(req, timeout=self.timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if self._is_empty_404(e):
                raise ConnectionError(
                    f"Yopu.co IP rate-limit block detected (empty HTTP 404 for {url}). "
                    f"Configure an egress via --egress 'ssh:<host>' or YOPU_EGRESS env."
                )
            raise ConnectionError(f"HTTP {e.code} error connecting to Yopu ({url}): {e.reason}")

    def fetch_with_session(self, init_url: str, target_z_path: str, referer: str) -> bytes:
        """
        Initializes session by visiting init_url (to obtain c=... cookie),
        then fetches target_z_path using the same egress and cookie jar.
        """
        headers = {
            "User-Agent": USER_AGENT,
            "Referer": referer,
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

        # 1. SSH egress (single atomic roundtrip)
        if self.egress and self.egress.lower().startswith("ssh:"):
            host = self.egress[4:].strip()
            target_url = urllib.parse.urljoin("https://yopu.co", target_z_path)
            cmd = f"""
J=$(mktemp)
curl -s --no-keepalive -c "$J" {shlex.quote(init_url)} > /dev/null
curl -s --no-keepalive --compressed -D - -b "$J" -H {shlex.quote(f'User-Agent: {USER_AGENT}')} -H {shlex.quote(f'Referer: {referer}')} -H 'Accept: */*' {shlex.quote(target_url)} | base64
rm -f "$J"
"""
            proc = subprocess.run(
                ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", host, cmd],
                capture_output=True, timeout=60
            )
            if proc.returncode != 0 and not proc.stdout:
                raise RuntimeError(f"SSH relay to {host} failed: {proc.stderr.decode('utf-8', 'replace')}")
            raw = base64.b64decode(proc.stdout)
            status, _, body = self._parse_http_dump(raw)
            if status != 200:
                raise ConnectionError(f"Egress {host} returned HTTP {status} for {target_z_path}")
            return body

        # 2. Proxy egress
        if self.egress and (self.egress.startswith("http") or self.egress.startswith("socks")):
            handler = urllib.request.ProxyHandler({"http": self.egress, "https": self.egress})
            opener = urllib.request.build_opener(handler, urllib.request.HTTPCookieProcessor(self.jar))
            opener.open(urllib.request.Request(init_url, headers=headers), timeout=self.timeout)
            target_url = urllib.parse.urljoin("https://yopu.co", target_z_path)
            with opener.open(urllib.request.Request(target_url, headers=headers), timeout=self.timeout) as resp:
                return resp.read()

        # 3. Direct
        try:
            self._opener.open(urllib.request.Request(init_url, headers=headers), timeout=self.timeout)
            target_url = urllib.parse.urljoin("https://yopu.co", target_z_path)
            with self._opener.open(urllib.request.Request(target_url, headers=headers), timeout=self.timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if self._is_empty_404(e):
                raise ConnectionError(
                    f"Yopu.co IP rate-limit block detected (empty HTTP 404). "
                    f"Configure an egress via --egress 'ssh:<host>' or YOPU_EGRESS env."
                )
            raise ConnectionError(f"HTTP {e.code} error from Yopu: {e.reason}")

    def search_scores(self, query: str, page: int = 0, instrument: str = "guitar") -> Dict[str, Any]:
        """Search Yopu.co for lead sheets matching query."""
        params = {
            "q": query.strip(),
            "page": page,
            "instrument": instrument
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

    def fetch_sheet_data(self, score_id_or_url: str) -> Dict[str, Any]:
        """
        Fetch full structured sheet data for a score ID from Yopu.co.
        Fetches /api/sheet?code=<id>&screen=1, then scoreUrlV4 for full measures.
        """
        score_id = extract_score_id(score_id_or_url)
        view_url = f"https://yopu.co/view/{score_id}"
        api_path = f"/api/sheet?code={score_id}&screen=1"
        z_path = encode_z(api_path)

        raw_bytes = self.fetch_with_session(
            init_url=view_url,
            target_z_path=z_path,
            referer=view_url
        )
        sheet_meta = decode_sheet_payload(raw_bytes)

        # Fetch scoreUrlV4 if present (CDN - direct fetch is always fine)
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
