"""
Unit tests for yopu.fetcher egress resolution and automatic fallback to direct connection.
"""
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from yopu.fetcher import resolve_egress, YopuClient


class TestYopuEgressResolution(unittest.TestCase):
    def test_explicit_direct(self):
        self.assertIsNone(resolve_egress("direct"))
        self.assertIsNone(resolve_egress("DIRECT"))
        self.assertIsNone(resolve_egress("  direct  "))

    def test_cli_egress_custom(self):
        self.assertEqual(resolve_egress("ssh:custom-host"), "ssh:custom-host")
        self.assertEqual(resolve_egress("socks5://127.0.0.1:1080"), "socks5://127.0.0.1:1080")

    def test_env_var_direct(self):
        with patch.dict(os.environ, {"YOPU_EGRESS": "direct"}):
            self.assertIsNone(resolve_egress())
        with patch.dict(os.environ, {"YOPU_EGRESS": "DIRECT"}):
            self.assertIsNone(resolve_egress())

    def test_env_var_custom(self):
        with patch.dict(os.environ, {"YOPU_EGRESS": "ssh:env-box"}):
            self.assertEqual(resolve_egress(), "ssh:env-box")

    def test_no_bleeding_into_yopu_pdf_when_primary_exists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            primary = Path(tmpdir) / ".config" / "yopu" / "egress"
            secondary = Path(tmpdir) / ".config" / "yopu-pdf" / "egress"
            primary.parent.mkdir(parents=True, exist_ok=True)
            secondary.parent.mkdir(parents=True, exist_ok=True)

            # Primary config exists with only comments
            primary.write_text("# Yopu Egress\n# ssh:my-vps\n# socks5:...\n", encoding="utf-8")
            # Secondary has active fallback
            secondary.write_text("vps:openclaw-eu\nproxy:vn\n", encoding="utf-8")

            with patch("pathlib.Path.home", return_value=Path(tmpdir)):
                with patch.dict(os.environ, {}, clear=True):
                    # Must NOT bleed through into yopu-pdf
                    resolved = resolve_egress()
                    self.assertIsNone(resolved)

    def test_primary_direct_keyword(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            primary = Path(tmpdir) / ".config" / "yopu" / "egress"
            primary.parent.mkdir(parents=True, exist_ok=True)
            primary.write_text("# config\ndirect\n", encoding="utf-8")

            with patch("pathlib.Path.home", return_value=Path(tmpdir)):
                with patch.dict(os.environ, {}, clear=True):
                    self.assertIsNone(resolve_egress())

    def test_primary_configured_host(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            primary = Path(tmpdir) / ".config" / "yopu" / "egress"
            primary.parent.mkdir(parents=True, exist_ok=True)
            primary.write_text("# config\nssh:primary-vps\n", encoding="utf-8")

            with patch("pathlib.Path.home", return_value=Path(tmpdir)):
                with patch.dict(os.environ, {}, clear=True):
                    self.assertEqual(resolve_egress(), "ssh:primary-vps")


class TestYopuClientFallback(unittest.TestCase):
    @patch("subprocess.run")
    def test_fetch_url_ssh_failure_falls_back_to_direct(self, mock_subproc):
        # Simulate SSH process failure (exit code 255)
        mock_proc = MagicMock()
        mock_proc.returncode = 255
        mock_proc.stdout = b""
        mock_proc.stderr = b"Connection refused"
        mock_subproc.return_value = mock_proc

        client = YopuClient(egress="ssh:bad-host")

        # Mock direct opener
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"<html>direct content</html>"
        mock_resp.__enter__.return_value = mock_resp
        mock_resp.__exit__.return_value = False

        with patch.object(client._opener, "open", return_value=mock_resp):
            body = client.fetch_url("https://yopu.co/test")
            self.assertEqual(body, b"<html>direct content</html>")
            self.assertTrue(mock_subproc.called)

    @patch("subprocess.run")
    def test_fetch_with_session_ssh_404_falls_back_to_direct(self, mock_subproc):
        import base64
        # Simulate SSH returning HTTP 404
        dump = b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
        b64_dump = base64.b64encode(dump)

        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = b64_dump
        mock_subproc.return_value = mock_proc

        client = YopuClient(egress="ssh:glintmuse")

        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"status": "direct_ok"}'
        mock_resp.__enter__.return_value = mock_resp
        mock_resp.__exit__.return_value = False

        with patch.object(client._opener, "open", return_value=mock_resp):
            body = client.fetch_with_session("https://yopu.co/explore", "/z/token", "https://yopu.co/")
            self.assertEqual(body, b'{"status": "direct_ok"}')
            self.assertTrue(mock_subproc.called)


if __name__ == "__main__":
    unittest.main()
