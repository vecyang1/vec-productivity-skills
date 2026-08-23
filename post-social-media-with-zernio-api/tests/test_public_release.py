from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def load_scanner():
    scanner_path = PACKAGE_ROOT / "release_checks" / "verify_public_release.py"
    spec = importlib.util.spec_from_file_location("verify_public_release", scanner_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load public-release scanner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PublicReleaseScannerTests(unittest.TestCase):
    def test_detects_private_content_without_echoing_values(self) -> None:
        scanner = load_scanner()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "sample.md").write_text(
                "ZERNIO_API_KEY=" + "sk_" + "a" * 64 + "\n"
                + "/" + "Users/private-user/runtime.env\n"
                + "person" + chr(64) + "private" + "." + "example\n"
                + "profileId=" + "66a1f0c2" + "a4b9d3e8f1a2b3c4\n",
                encoding="utf-8",
            )

            findings = scanner.scan_working_tree(root)

        categories = {finding.category for finding in findings}
        self.assertEqual(
            categories,
            {
                "live Zernio credential",
                "local-machine path",
                "non-example email",
                "concrete Zernio identifier",
            },
        )
        self.assertTrue(all("sk_" not in finding.path for finding in findings))

    def test_history_audit_resolves_nested_package_paths(self) -> None:
        scanner = load_scanner()
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "collection"
            package = repo / "nested-package"
            package.mkdir(parents=True)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test" + chr(64) + "example.com"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
            target = package / "SKILL.md"
            target.write_text("/" + "Users/private-user/runtime.env\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "leak"], check=True)
            target.write_text("Use ZERNIO_API_KEY from the environment.\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "sanitize"], check=True)

            findings = scanner.scan_reachable_history(package)

        self.assertEqual([(finding.category, finding.path) for finding in findings], [("local-machine path", "SKILL.md")])


if __name__ == "__main__":
    unittest.main()
