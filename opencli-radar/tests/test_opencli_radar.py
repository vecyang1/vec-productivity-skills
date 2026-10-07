#!/usr/bin/env python3
"""test_opencli_radar.py — Unit tests for opencli-radar discovery, triage, and diagnosis."""
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import opencli_radar


class TestOpenCLIRadarNormalization(unittest.TestCase):
    def test_normalize_target_site_urls(self):
        self.assertEqual(opencli_radar.normalize_target_site("https://x.com/home"), "twitter")
        self.assertEqual(opencli_radar.normalize_target_site("https://twitter.com"), "twitter")
        self.assertEqual(opencli_radar.normalize_target_site("https://www.bilibili.com/video/123"), "bilibili")
        self.assertEqual(opencli_radar.normalize_target_site("https://goofish.com/item/456"), "xianyu")
        self.assertEqual(opencli_radar.normalize_target_site("https://claspo.io/features"), "claspo")

    def test_normalize_target_site_names_and_aliases(self):
        self.assertEqual(opencli_radar.normalize_target_site("opencli-plugin-claspo"), "claspo")
        self.assertEqual(opencli_radar.normalize_target_site("opencli-adapter-github"), "github")
        self.assertEqual(opencli_radar.normalize_target_site("goofish"), "xianyu")
        self.assertEqual(opencli_radar.normalize_target_site("xy"), "xianyu")
        self.assertEqual(opencli_radar.normalize_target_site("xhs"), "xiaohongshu")
        self.assertEqual(opencli_radar.normalize_target_site("tweet"), "twitter")


class TestOpenCLIRadarCollisionExclusion(unittest.TestCase):
    def test_excludes_openapi_generators(self):
        self.assertFalse(opencli_radar.is_legitimate_opencli_repo("xyd-js/openapi2opencli"))
        self.assertFalse(opencli_radar.is_legitimate_opencli_repo("xyd-js/opencli2go"))
        self.assertFalse(opencli_radar.is_legitimate_opencli_repo("openclidev/specification"))

    def test_excludes_unrelated_substring_matches(self):
        self.assertFalse(opencli_radar.is_legitimate_opencli_repo("someone/openclip-model"))
        self.assertFalse(opencli_radar.is_legitimate_opencli_repo("org/openclimate-tracker"))

    def test_accepts_legitimate_community_repos(self):
        self.assertTrue(opencli_radar.is_legitimate_opencli_repo("SlowGrowth1314/opencli-weixin-album"))
        self.assertTrue(opencli_radar.is_legitimate_opencli_repo("vecyang1/opencli-plugin-claspo"))
        self.assertTrue(opencli_radar.is_legitimate_opencli_repo("user/opencli-adapter-douyin"))


class TestOpenCLIRadarTriage(unittest.TestCase):
    def test_unlicensed_repo_gets_read_only(self):
        candidate = {
            "name": "opencli-plugin-test",
            "repo_url": "https://github.com/example/opencli-plugin-test",
            "license_spdx": None,
            "stars": 10,
        }
        res = opencli_radar.triage_candidate(candidate)
        self.assertEqual(res["verdict"], "READ_ONLY")
        self.assertFalse(res["has_license"])
        self.assertIn("All Rights Reserved", res["verdict_reason"])

    def test_active_mit_repo_gets_install(self):
        candidate = {
            "name": "opencli-plugin-test",
            "repo_url": "https://github.com/example/opencli-plugin-test",
            "license_spdx": "MIT",
            "stars": 25,
            "pushed_at": "2026-10-01T00:00:00Z",
        }
        res = opencli_radar.triage_candidate(candidate)
        self.assertEqual(res["verdict"], "INSTALL")
        self.assertTrue(res["is_open_source"])

    def test_inactive_open_source_gets_fork_and_vendor(self):
        candidate = {
            "name": "opencli-plugin-dormant",
            "repo_url": "https://github.com/example/opencli-plugin-dormant",
            "license_spdx": "Apache-2.0",
            "stars": 1,
            "pushed_at": "2024-01-01T00:00:00Z",
        }
        res = opencli_radar.triage_candidate(candidate)
        self.assertEqual(res["verdict"], "FORK_AND_VENDOR")
        self.assertIn("unmaintained", res["verdict_reason"])


class TestOpenCLIRadarDiagnosis(unittest.TestCase):
    def test_diagnose_local_match(self):
        local_inv = {
            "twitter": {
                "site": "twitter",
                "canonical_site": "twitter",
                "source": "local_builtin",
                "commands": ["post", "timeline"],
            }
        }
        diag = opencli_radar.diagnose_site("https://twitter.com", local_inventory=local_inv, community_inventory=[])
        self.assertEqual(diag["verdict"], "REUSE_LOCAL")
        self.assertIn("opencli twitter", diag["actionable_command"])

    def test_diagnose_community_match(self):
        community_inv = [
            {
                "name": "opencli-plugin-foo",
                "canonical_site": "foo",
                "repo_url": "https://github.com/example/opencli-plugin-foo",
                "stars": 15,
                "license_spdx": "MIT",
                "verdict": "INSTALL",
                "verdict_reason": "Active open-source plugin",
            }
        ]
        diag = opencli_radar.diagnose_site("foo", local_inventory={}, community_inventory=community_inv)
        self.assertEqual(diag["verdict"], "INSTALL")
        self.assertIn("opencli plugin install github:example/opencli-plugin-foo", diag["actionable_command"])

    def test_diagnose_missing_site_yields_build_new(self):
        diag = opencli_radar.diagnose_site("nonexistentplatformxyz123", local_inventory={}, community_inventory=[])
        self.assertEqual(diag["verdict"], "BUILD_NEW")
        self.assertIn("opencli browser init", diag["actionable_command"])


if __name__ == "__main__":
    unittest.main()
