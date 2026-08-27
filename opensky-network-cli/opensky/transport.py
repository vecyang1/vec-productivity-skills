"""
Transport chokepoint for all OpenSky Network API communication.
Guarantees:
- Single place for credential ingestion and OAuth2 Bearer token lifecycle.
- In-memory and disk token caching to prevent token exhaustion.
- Automatic DNS fallback resolution (self-healing for regional DNS anomalies).
- Live tracking and parsing of X-Rate-Limit-Remaining headers.
- Graceful 429 Rate Limit error formatting.
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .models import RateLimitStatus
from .resolver import resolve_credentials

AUTH_TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
API_BASE_URL = "https://opensky-network.org/api"
TOKEN_CACHE_FILE = Path.home() / ".cache" / "opensky" / "token_cache.json"

# DNS self-healing state
_DNS_PATCHED = False
_ORIG_GETADDRINFO = socket.getaddrinfo


def _setup_dns_resilience():
    """Install transparent DNS fallback to 1.1.1.1/8.8.8.8 if local DNS fails."""
    global _DNS_PATCHED
    if _DNS_PATCHED:
        return

    def _resilient_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        try:
            return _ORIG_GETADDRINFO(host, port, family, type, proto, flags)
        except socket.gaierror:
            # Try public DNS query via dig
            if shutil.which("dig"):
                for dns_server in ("1.1.1.1", "8.8.8.8"):
                    try:
                        res = subprocess.run(
                            ["dig", f"@{dns_server}", host, "+short"],
                            capture_output=True,
                            text=True,
                            timeout=2.5,
                        )
                        ips = [
                            line.strip()
                            for line in res.stdout.splitlines()
                            if line.strip() and not line.startswith(";")
                        ]
                        if ips:
                            # Use resolved IP with orig getaddrinfo
                            return _ORIG_GETADDRINFO(ips[0], port, family, type, proto, flags)
                    except Exception:
                        continue
            raise

    socket.getaddrinfo = _resilient_getaddrinfo
    _DNS_PATCHED = True


class OpenSkyTransport:
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        timeout: float = 12.0,
    ):
        _setup_dns_resilience()
        self.timeout = timeout
        self.client_id, self.client_secret, self.auth_source = resolve_credentials(
            custom_client_id=client_id,
            custom_client_secret=client_secret,
        )
        self._cached_token: Optional[str] = None
        self._token_expiry: float = 0.0
        self.last_rate_limit: RateLimitStatus = RateLimitStatus(
            remaining_credits=None,
            daily_allowance=4000 if self.client_id else 400,
            retry_after_seconds=None,
            auth_mode=self.auth_source,
            token_valid_until=None,
        )
        self._load_disk_token()

    def _load_disk_token(self) -> None:
        """Load valid cached OAuth token from local disk."""
        if not self.client_id:
            return
        if TOKEN_CACHE_FILE.is_file():
            try:
                with open(TOKEN_CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("client_id") == self.client_id:
                        expires_at = data.get("expires_at", 0)
                        if expires_at > time.time() + 60:
                            self._cached_token = data.get("access_token")
                            self._token_expiry = expires_at
                            self.last_rate_limit.token_valid_until = expires_at
            except Exception:
                pass

    def _save_disk_token(self, token: str, expires_in: int) -> None:
        """Persist valid OAuth token to disk cache."""
        try:
            TOKEN_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            expires_at = time.time() + expires_in
            self._cached_token = token
            self._token_expiry = expires_at
            self.last_rate_limit.token_valid_until = expires_at
            with open(TOKEN_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "client_id": self.client_id,
                    "access_token": token,
                    "expires_at": expires_at,
                }, f)
        except Exception:
            pass

    def get_valid_token(self) -> Optional[str]:
        """Obtain a valid OAuth2 Bearer token, refreshing if necessary."""
        if not self.client_id or not self.client_secret:
            return None

        if self._cached_token and self._token_expiry > time.time() + 60:
            return self._cached_token

        # Fetch fresh token via client_credentials flow
        post_data = urllib.parse.urlencode({
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }).encode("utf-8")

        req = urllib.request.Request(
            AUTH_TOKEN_URL,
            data=post_data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "OpenSkyCLI/1.0 (AgentAutomation)",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                token = resp_data.get("access_token")
                expires_in = int(resp_data.get("expires_in", 1800))
                if token:
                    self._save_disk_token(token, expires_in)
                    return token
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"OpenSky OAuth2 Authentication failed (HTTP {e.code}): {err_msg}")
        except Exception as ex:
            raise RuntimeError(f"Network error authenticating with OpenSky OAuth server: {ex}")

        return None

    def request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
    ) -> Tuple[Any, RateLimitStatus]:
        """
        Execute API request through the single transport chokepoint.
        """
        clean_endpoint = endpoint.lstrip("/")
        url = f"{API_BASE_URL}/{clean_endpoint}"
        if params:
            clean_params = {k: v for k, v in params.items() if v is not None}
            if clean_params:
                url += "?" + urllib.parse.urlencode(clean_params)

        headers = {
            "User-Agent": "OpenSkyCLI/1.0 (AgentAutomation)",
            "Accept": "application/json",
        }

        # Attach Bearer token if credentials exist
        if self.client_id and self.client_secret:
            try:
                token = self.get_valid_token()
                if token:
                    headers["Authorization"] = f"Bearer {token}"
            except Exception as e:
                sys.stderr.write(f"[WARN] Token refresh error: {e}\n")

        req = urllib.request.Request(url, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw_body = resp.read().decode("utf-8")
                headers_dict = dict(resp.headers)

                # Parse Rate Limit Headers
                rem_credits = headers_dict.get("X-Rate-Limit-Remaining") or headers_dict.get("x-rate-limit-remaining")
                retry_after = headers_dict.get("X-Rate-Limit-Retry-After-Seconds") or headers_dict.get("x-rate-limit-retry-after-seconds")

                if rem_credits and str(rem_credits).isdigit():
                    self.last_rate_limit.remaining_credits = int(rem_credits)
                if retry_after and str(retry_after).isdigit():
                    self.last_rate_limit.retry_after_seconds = int(retry_after)

                parsed_json = json.loads(raw_body) if raw_body else {}
                return parsed_json, self.last_rate_limit

        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            headers_dict = dict(e.headers) if hasattr(e, "headers") else {}
            rem_credits = headers_dict.get("X-Rate-Limit-Remaining") or headers_dict.get("x-rate-limit-remaining")
            retry_after = headers_dict.get("X-Rate-Limit-Retry-After-Seconds") or headers_dict.get("x-rate-limit-retry-after-seconds")

            if rem_credits and str(rem_credits).isdigit():
                self.last_rate_limit.remaining_credits = int(rem_credits)
            if retry_after and str(retry_after).isdigit():
                self.last_rate_limit.retry_after_seconds = int(retry_after)

            if e.code == 429:
                wait_sec = self.last_rate_limit.retry_after_seconds or 60
                raise RuntimeError(
                    f"OpenSky API Rate Limit Exceeded (HTTP 429). Remaining credits: {self.last_rate_limit.remaining_credits}. "
                    f"Please wait {wait_sec} seconds before retrying."
                )
            elif e.code in (401, 403):
                raise RuntimeError(
                    f"OpenSky API Authentication Error (HTTP {e.code}): {err_body}. "
                    f"Verify Client ID/Secret in 1Password or .env file."
                )
            elif e.code == 404:
                return {}, self.last_rate_limit
            else:
                raise RuntimeError(f"OpenSky API Error (HTTP {e.code}): {err_body}")

        except urllib.error.URLError as ue:
            raise RuntimeError(f"Failed to connect to OpenSky Network ({url}): {ue.reason}")
        except Exception as ex:
            raise RuntimeError(f"Unexpected error calling OpenSky Network API: {ex}")
