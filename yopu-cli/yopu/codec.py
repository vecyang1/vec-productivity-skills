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


def decode_z(z_path: str) -> str:
    """
    Decodes an obfuscated '/z/<token>' path back into its internal endpoint path.
    """
    token = z_path[3:] if z_path.startswith("/z/") else z_path
    b64_map = {c: i for i, c in enumerate(_B64_ALPHABET)}
    vals = [b64_map[c] for c in token if c in b64_map]
    raw = bytearray()
    i = 0
    while i < len(vals):
        o = vals[i]
        a = vals[i + 1] if i + 1 < len(vals) else 0
        s = vals[i + 2] if i + 2 < len(vals) else 0
        h = vals[i + 3] if i + 3 < len(vals) else 0
        raw.append((o << 2) | (a >> 4))
        if i + 2 < len(vals):
            raw.append(((15 & a) << 4) | (s >> 2))
        if i + 3 < len(vals):
            raw.append(((3 & s) << 6) | h)
        i += 4

    length = len(raw)
    prng = _ZPRNG(length)
    swaps = []
    for r in range(length - 1, 0, -1):
        prng.u()
        swaps.append((r, int(prng.rnd() * (r + 1))))
    for r, target in reversed(swaps):
        raw[r], raw[target] = raw[target], raw[r]

    for idx in range(len(raw)):
        raw[idx] ^= 92

    return raw.decode("utf-8", errors="replace")


def compute_sheet_t(st: str, key: str = "SdZWq_H3OXnrFgPLwk9kow") -> str:
    """
    Computes the dynamic query token `t` required for `/api/sheet?...&t=...&v=2`
    from the session token `st` extracted from HTML `data-model`.
    Algorithm: XOR with repeating key, W-permutation, custom URL-safe Base64.
    """
    raw = bytearray(st.encode("utf-8"))
    k_bytes = key.encode("utf-8")
    for i in range(len(raw)):
        raw[i] ^= k_bytes[i % len(k_bytes)]

    # W-permutation
    length = len(raw)
    prng = _z_mod(length, _Z_K)
    for i in range(length - 1, 0, -1):
        prng = _z_mod(_Z_J * prng + _Z_W, _Z_K)
        target = int((prng / _Z_K) * (i + 1))
        raw[i], raw[target] = raw[target], raw[i]

    # Custom base64 encode
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
    return "".join(out)



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


_L_CONST = "ə\vĀ"
_R_CONST = ord(_L_CONST[0])  # 601
_G_CONST = ord(_L_CONST[1])  # 11
_U_CONST = ord(_L_CONST[2]) * ord(_L_CONST[2])  # 65536


def _h_const() -> int:
    e, i = _U_CONST, _z_mod(_R_CONST, _U_CONST)
    o, r = 0, 1
    while i != 0:
        u = e // i
        e, i = i, e - u * i
        o, r = r, o - u * r
    return _z_mod(o, _U_CONST)


_H_CONST = _h_const()


def _pow_mod(t: int, n: int, e: int) -> int:
    i = 1
    o = _z_mod(t, e)
    while n > 0:
        t_val = _z_mod(n, 2)
        n = n // 2
        if t_val == 1:
            i = _z_mod(i * o, e)
        o = _z_mod(o * o, e)
    return i


class _PermPRNG:
    def __init__(self, t: int = 1):
        self.n = _z_mod(t, _U_CONST)

    def s(self) -> float:
        return self.n / _U_CONST

    def t_step(self) -> None:
        self.n = _z_mod(_H_CONST * (self.n - _G_CONST), _U_CONST)

    def x_step(self, t: int) -> None:
        e = ((_pow_mod(_R_CONST, t, _R_CONST * _U_CONST - _U_CONST) - 1) // (_R_CONST - 1)) * _G_CONST
        i = _pow_mod(_R_CONST, t, _U_CONST) * self.n
        self.n = _z_mod(e + i, _U_CONST)


def _permute_v(arr: bytearray) -> None:
    n = len(arr)
    prng = _PermPRNG(n)
    prng.x_step(n)
    for r in range(1, n):
        prng.t_step()
        i = int(prng.s() * (r + 1))
        arr[r], arr[i] = arr[i], arr[r]


def decode_data_model(encoded_str: str) -> Dict[str, Any]:
    """
    Decodes the URL-encoded and obfuscated `data-model` attribute embedded in Yopu score HTML.
    Extracts session tokens such as `model.st` required for /api/sheet requests.
    """
    import urllib.parse
    unquoted = urllib.parse.unquote(encoded_str)
    raw = bytearray(ord(c) ^ 171 for c in unquoted)
    _permute_v(raw)
    return json.loads(raw.decode("utf-8", errors="replace"))

