from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str):
    module_path = PACKAGE_ROOT / "scripts" / f"{name}.py"
    sys.path.insert(0, str(module_path.parent))
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ZernioHelperTests(unittest.TestCase):
    def test_publish_payload_keeps_caption_and_uses_exact_targets(self) -> None:
        post_content = load_module("post_content")
        payload = post_content.build_payload(
            caption="Approved caption.",
            platforms=["twitter", "linkedin"],
            account_ids=["account-a", "account-b"],
            media_items=[{"url": "https://media.example/photo.jpg", "type": "image"}],
        )

        self.assertEqual(payload["content"], "Approved caption.")
        self.assertTrue(payload["publishNow"])
        self.assertEqual(
            payload["platforms"],
            [
                {"platform": "twitter", "accountId": "account-a"},
                {"platform": "linkedin", "accountId": "account-b"},
            ],
        )

    def test_publish_payload_rejects_ambiguous_targets(self) -> None:
        post_content = load_module("post_content")
        with self.assertRaises(ValueError):
            post_content.build_payload(
                caption="Approved caption.",
                platforms=["twitter", "linkedin"],
                account_ids=["account-a"],
                media_items=[],
            )

    def test_account_filter_fails_closed_when_exact_target_is_missing(self) -> None:
        verify_connection = load_module("verify_connection")
        accounts = [
            {"_id": "account-a", "platform": "twitter"},
            {"_id": "account-b", "platform": "linkedin"},
        ]

        selected = verify_connection.select_exact_accounts(
            accounts,
            platforms=["twitter"],
            account_ids=["account-a"],
        )
        self.assertEqual(selected, [{"_id": "account-a", "platform": "twitter"}])
        with self.assertRaises(ValueError):
            verify_connection.select_exact_accounts(
                accounts,
                platforms=["twitter"],
                account_ids=["missing-account"],
            )


if __name__ == "__main__":
    unittest.main()
