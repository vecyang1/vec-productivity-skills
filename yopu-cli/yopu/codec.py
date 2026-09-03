"""
Codec and cryptographic transformations for Yopu.co API endpoints.

Handles:
- /z/<path> obfuscation of internal /api/... routes
- XOR 157 decoding of search results
- V(e) permutation and Brotli custom dictionary decompression for sheet data
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List

# Bundle constants from yopu.co: y = 'ə\vĀ'
_Z_J = 601
_Z_W = 11
_Z_K = 65536  # 256 * 256
_B64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
_PREFIXES = ("/api/", "/i/", "/auth/", "/promotion/", "/ping/", "/ping-user/")


def _z_mod(t: int, n: int) -> int:
    r = t % n
    return r + n if r < 0 else r


def _egcd(t: int, e: int) -> int:
    r0, r1 = e, _z_mod(t, e)
    a0, a1 = 0, 1
    while r1 != 0:
        u = r0 // r1
        r0, r1 = r1, r0 - u * r1
        a0, a1 = a1, a0 - u * a1
    return _z_mod(a0, e)


class _ZPRNG:
    def __init__(self, seed: int = 1):
        self.t = _z_mod(seed, _Z_K)

    def u(self) -> None:
        self.t = _z_mod(_Z_J * self.t + _Z_W, _Z_K)

    def rnd(self) -> float:
        return self.t / _Z_K


def _swap(arr: bytearray, e: int, n: float) -> None:
    r = int(n * (e + 1))
    arr[e], arr[r] = arr[r], arr[e]


def encode_z(path: str) -> str:
    """
    Transforms an internal endpoint path (e.g. '/api/search/sheets?q=...')
    into the obfuscated '/z/<token>' path required by Yopu.co's edge gateway.
    """
    should_encode = any(path.startswith(prefix) for prefix in _PREFIXES)
    if not should_encode:
        return path

    # UTF-8 encode and XOR with 92 (0x5C)
    raw = bytearray(path.encode("utf-8"))
    for i in range(len(raw)):
        raw[i] ^= 92

    # Fisher-Yates shuffle seeded with byte length
    length = len(raw)
    prng = _ZPRNG(length)
    for r in range(length - 1, 0, -1):
        prng.u()
        _swap(raw, r, prng.rnd())

    # Base64 with custom URL-safe alphabet
    out = []
    i = 0
    while i < length:
        has_next = (i + 1) < length
        has_third = (i + 2) < length
        o = raw[i]
        a = raw[i + 1] if has_next else 0
        s = raw[i + 2] if has_third else 0

        out.append(_B64_ALPHABET[o >> 2])
        out.append(_B64_ALPHABET[((3 & o) << 4) | (a >> 4)])
        if not has_next:
            break
        out.append(_B64_ALPHABET[((15 & a) << 2) | (s >> 6)])
        if not has_third:
            break
        out.append(_B64_ALPHABET[63 & s])
        i += 3

    return "/z/" + "".join(out)


def decode_search_response(raw_bytes: bytes) -> Dict[str, Any]:
    """
    Decodes the XOR 157 (0x9D) obfuscated search response payload from Yopu.co.
    """
    decoded_bytes = bytes(b ^ 157 for b in raw_bytes)
    return json.loads(decoded_bytes.decode("utf-8", errors="replace"))


def decode_sheet_payload(raw_bytes: bytes) -> Dict[str, Any]:
    """
    Decodes the binary /api/sheet or scoreUrlV4 response (V permutation + q7 Brotli decompression).
    Uses the local Node.js decoder bridge.
    """
    decoder_script = Path(__file__).parent / "decoder.cjs"
    if not decoder_script.exists():
        raise FileNotFoundError(f"Decoder bridge not found: {decoder_script}")

    proc = subprocess.run(
        ["node", str(decoder_script)],
        input=raw_bytes,
        capture_output=True,
        check=False
    )
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"Failed to decompress Yopu sheet payload (code {proc.returncode}): {err}")

    output_text = proc.stdout.decode("utf-8", errors="replace")
    return json.loads(output_text)
