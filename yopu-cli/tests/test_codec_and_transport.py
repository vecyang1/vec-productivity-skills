"""
Unit tests for Yopu codec and transport routines.
"""
import unittest
from pathlib import Path
from yopu.codec import encode_z, decode_search_response, decode_sheet_payload
from yopu.fetcher import extract_score_id, build_score_url, resolve_egress


class TestYopuCodec(unittest.TestCase):
    def test_encode_z_prefix_filter(self):
        # Non-matching paths should remain unchanged
        self.assertEqual(encode_z("/view/aXYaaOXZ"), "/view/aXYaaOXZ")
        self.assertEqual(encode_z("https://cdn.yopu.co/nier4/abc"), "https://cdn.yopu.co/nier4/abc")

    def test_encode_z_deterministic_transformation(self):
        api_path = "/api/search/sheets?q=晴天&page=0&instrument=guitar"
        z_path = encode_z(api_path)
        self.assertTrue(z_path.startswith("/z/"))
        token = z_path[3:]
        # Must only contain characters from custom base64 alphabet
        valid_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")
        self.assertTrue(all(c in valid_chars for c in token))

    def test_decode_search_response(self):
        # Synthetic XOR 157 payload of '{"totalResultNum": 1, "results": []}'
        original_json = b'{"totalResultNum": 1, "results": []}'
        xor_bytes = bytes(b ^ 157 for b in original_json)
        data = decode_search_response(xor_bytes)
        self.assertEqual(data["totalResultNum"], 1)
        self.assertEqual(data["results"], [])

    def test_extract_score_id(self):
        self.assertEqual(extract_score_id("https://yopu.co/view/aPenOOpb"), "aPenOOpb")
        self.assertEqual(extract_score_id("https://yopu.co/sheet/aXYaaOXZ"), "aXYaaOXZ")
        self.assertEqual(extract_score_id("aXYaaOXZ"), "aXYaaOXZ")
        self.assertEqual(extract_score_id("aPenOOpb?from=share"), "aPenOOpb")

    def test_build_score_url(self):
        self.assertEqual(build_score_url("aPenOOpb"), "https://yopu.co/view/aPenOOpb")
        self.assertEqual(build_score_url("https://yopu.co/view/aPenOOpb"), "https://yopu.co/view/aPenOOpb")

    def test_resolve_egress_priority(self):
        # CLI priority
        self.assertEqual(resolve_egress("ssh:custom-host"), "ssh:custom-host")


if __name__ == "__main__":
    unittest.main()
