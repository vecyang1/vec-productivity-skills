"""Small standard-library Zernio HTTP client used by the public helpers."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = "https://zernio.com/api/v1"


@dataclass(frozen=True)
class APIError(RuntimeError):
    status: int | None
    error_type: str | None
    code: str | None

    def __str__(self) -> str:
        fields = [
            f"HTTP {self.status}" if self.status is not None else "network error",
            self.error_type or "unknown_error",
            self.code or "unknown_code",
        ]
        return ": ".join(fields)


def get_api_key() -> str:
    key = os.environ.get("ZERNIO_API_KEY", "").strip()
    if not key:
        raise ValueError("ZERNIO_API_KEY is required; set it in the process environment")
    return key


def request_json(method: str, path: str, *, payload: dict[str, Any] | None = None, query: str = "", request_id: str | None = None) -> tuple[int, dict[str, Any]]:
    url = f"{BASE_URL}{path}{query}"
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Authorization": f"Bearer {get_api_key()}", "Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if request_id:
        headers["x-request-id"] = request_id
    request = Request(url, data=body, headers=headers, method=method.upper())
    try:
        with urlopen(request, timeout=30) as response:
            raw_body = response.read().decode("utf-8")
            parsed = json.loads(raw_body) if raw_body else {}
            return response.status, parsed if isinstance(parsed, dict) else {"data": parsed}
    except HTTPError as exc:
        try:
            error_body = json.loads(exc.read().decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            error_body = {}
        raise APIError(exc.code, error_body.get("type"), error_body.get("code")) from exc
    except URLError as exc:
        raise APIError(None, "network_error", None) from exc
