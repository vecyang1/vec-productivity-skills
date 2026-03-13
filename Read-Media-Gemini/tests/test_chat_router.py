import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
CHAT_SCRIPT = ROOT / "scripts" / "chat.py"


class FakeResponse:
    def __init__(self, status_code, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text

    def json(self):
        return self._json_data


class EnvOverride:
    def __init__(self, values):
        self.values = values
        self.previous = {}

    def __enter__(self):
        for key, value in self.values.items():
            self.previous[key] = os.environ.get(key)
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key, old_value in self.previous.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value


def load_chat_module():
    spec = importlib.util.spec_from_file_location("chat_module_under_test", CHAT_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def create_temp_jpg(content):
    fd, path = tempfile.mkstemp(suffix=".jpg")
    os.close(fd)
    with open(path, "wb") as handle:
        handle.write(content)
    return path


class ChatProviderRoutingTests(unittest.TestCase):
    def setUp(self):
        self.default_env = {
            "PRIMARY_PROVIDER": "kie",
            "KIE_API_KEY": "kie-test-key",
            "KIE_MODEL": "gemini-3-flash",
            "KIE_BASE_URL": "https://api.kie.ai/gemini-3-flash/v1/chat/completions",
            "GOOGLE_API_KEY": "google-test-key",
            "GOOGLE_MODEL": "gemini-3-flash-preview",
        }

    def test_kie_is_prioritized_and_accepts_multiple_images(self):
        image_one = create_temp_jpg(b"\xff\xd8\xff\xdbtest-image-1")
        image_two = create_temp_jpg(b"\xff\xd8\xff\xdbtest-image-2")
        self.addCleanup(lambda: os.path.exists(image_one) and os.remove(image_one))
        self.addCleanup(lambda: os.path.exists(image_two) and os.remove(image_two))

        with EnvOverride(self.default_env):
            chat = load_chat_module()

            def fake_post(url, headers=None, json=None, timeout=120):
                self.assertEqual(url, chat.KIE_BASE_URL)
                self.assertEqual(json["model"], "gemini-3-flash")
                content = json["messages"][0]["content"]
                image_items = [part for part in content if part.get("type") == "image_url"]
                text_items = [part for part in content if part.get("type") == "text"]
                self.assertEqual(len(image_items), 2)
                self.assertEqual(len(text_items), 1)
                self.assertTrue(
                    image_items[0]["image_url"]["url"].startswith("data:image/jpeg;base64,")
                )
                return FakeResponse(
                    200,
                    {"choices": [{"message": {"content": "KIE success"}}]},
                )

            with patch.object(chat.requests, "post", side_effect=fake_post) as post_mock:
                ok = chat.chat("Compare these images", [image_one, image_two], "image")

            self.assertTrue(ok)
            self.assertEqual(post_mock.call_count, 1)

    def test_kie_failure_falls_back_to_google(self):
        image_one = create_temp_jpg(b"\xff\xd8\xff\xdbtest-image-fallback")
        self.addCleanup(lambda: os.path.exists(image_one) and os.remove(image_one))

        with EnvOverride(self.default_env):
            chat = load_chat_module()
            calls = []

            def fake_post(url, headers=None, json=None, timeout=120):
                calls.append(url)
                if url == chat.KIE_BASE_URL:
                    return FakeResponse(503, text="Service unavailable")
                self.assertIn("generativelanguage.googleapis.com", url)
                parts = json["contents"][0]["parts"]
                inline_parts = [part for part in parts if "inline_data" in part]
                self.assertEqual(len(inline_parts), 1)
                return FakeResponse(
                    200,
                    {
                        "candidates": [
                            {"content": {"parts": [{"text": "Google fallback success"}]}}
                        ]
                    },
                )

            with patch.object(chat.requests, "post", side_effect=fake_post):
                ok = chat.chat("Analyze image", [image_one], "image")

            self.assertTrue(ok)
            self.assertEqual(calls, [chat.KIE_BASE_URL, chat.get_google_url()])

    def test_returns_false_when_no_provider_key_available(self):
        with EnvOverride(
            {
                "PRIMARY_PROVIDER": "kie",
                "KIE_API_KEY": "",
                "GOOGLE_API_KEY": "",
                "KIE_MODEL": "gemini-3-flash",
                "GOOGLE_MODEL": "gemini-3-flash-preview",
            }
        ):
            chat = load_chat_module()
            ok = chat.chat("Hello")
            self.assertFalse(ok)

    def test_google_payload_supports_multiple_images(self):
        image_one = create_temp_jpg(b"\xff\xd8\xff\xdbimg1")
        image_two = create_temp_jpg(b"\xff\xd8\xff\xdbimg2")
        self.addCleanup(lambda: os.path.exists(image_one) and os.remove(image_one))
        self.addCleanup(lambda: os.path.exists(image_two) and os.remove(image_two))

        with EnvOverride(
            {
                "PRIMARY_PROVIDER": "google",
                "KIE_API_KEY": "",
                "GOOGLE_API_KEY": "google-test-key",
                "GOOGLE_MODEL": "gemini-3-flash-preview",
                "KIE_MODEL": "gemini-3-flash",
            }
        ):
            chat = load_chat_module()

            def fake_post(url, headers=None, json=None, timeout=120):
                self.assertEqual(url, chat.get_google_url())
                parts = json["contents"][0]["parts"]
                inline_parts = [part for part in parts if "inline_data" in part]
                text_parts = [part for part in parts if "text" in part]
                self.assertEqual(len(inline_parts), 2)
                self.assertEqual(len(text_parts), 1)
                return FakeResponse(
                    200,
                    {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]},
                )

            with patch.object(chat.requests, "post", side_effect=fake_post):
                ok = chat.chat("Compare", [image_one, image_two], "image")

            self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
