from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "verify_public_release.py"


def load_auditor():
    return load_module().audit_directory


def load_history_auditor():
    return load_module().audit_reachable_history


def load_module():
    spec = importlib.util.spec_from_file_location("verify_public_release", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublicReleaseAuditTests(unittest.TestCase):
    def test_reports_live_secrets_and_private_locators_without_echoing_them(self) -> None:
        audit_directory = load_auditor()

        with tempfile.TemporaryDirectory() as temporary_directory:
            package = Path(temporary_directory)
            (package / "safe.md").write_text("Set NOTION_TOKEN in your environment.\n")
            (package / "unsafe.md").write_text(
                "\n".join(
                    [
                        "token=" + "ntn_" + "a" * 24,
                        "path=" + "/" + "Users/" + "person/private.env",
                        "database=" + "a" * 32,
                        "contact=" + "person@" + "private.example",
                    ]
                )
            )

            findings = audit_directory(package)

        self.assertEqual(
            findings,
            {
                "unsafe.md": [
                    "live Notion token",
                    "local-machine path",
                    "Notion-style identifier",
                    "non-example email address",
                ]
            },
        )

    def test_allows_documented_environment_variable_and_example_values(self) -> None:
        audit_directory = load_auditor()

        with tempfile.TemporaryDirectory() as temporary_directory:
            package = Path(temporary_directory)
            (package / "README.md").write_text(
                "\n".join(
                    [
                        "export NOTION_TOKEN=your_integration_token_here",
                        "Database ID: your-database-id-here",
                        "Contact: maintainer@example.com",
                    ]
                )
            )

            findings = audit_directory(package)

        self.assertEqual(findings, {})

    def test_ignores_generated_python_cache(self) -> None:
        audit_directory = load_auditor()

        with tempfile.TemporaryDirectory() as temporary_directory:
            package = Path(temporary_directory)
            generated = package / "__pycache__"
            generated.mkdir()
            (generated / "cache.pyc").write_text("path=" + "/" + "Users/" + "person/private.env")

            findings = audit_directory(package)

        self.assertEqual(findings, {})

    def test_ignores_derived_graph_artifacts(self) -> None:
        audit_directory = load_auditor()

        with tempfile.TemporaryDirectory() as temporary_directory:
            package = Path(temporary_directory)
            generated = package / "graphify-out"
            generated.mkdir()
            (generated / "graph.json").write_text("source=" + "/" + "Users/" + "person/private.env")

            findings = audit_directory(package)

        self.assertEqual(findings, {})

    def test_audits_history_from_a_nested_package_root(self) -> None:
        audit_reachable_history = load_history_auditor()

        with tempfile.TemporaryDirectory() as temporary_directory:
            collection = Path(temporary_directory) / "collection"
            package = collection / "notion-mcp-connector"
            package.mkdir(parents=True)
            subprocess.run(["git", "init", str(collection)], check=True, stdout=subprocess.DEVNULL)
            (package / "SKILL.md").write_text("# Safe package\n")
            subprocess.run(["git", "-C", str(collection), "add", "notion-mcp-connector/SKILL.md"], check=True)
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(collection),
                    "-c",
                    "user.name=Public Release Test",
                    "-c",
                    "user.email=maintainer@example.com",
                    "commit",
                    "-m",
                    "add safe package",
                ],
                check=True,
                stdout=subprocess.DEVNULL,
            )

            findings = audit_reachable_history(package)

        self.assertEqual(findings, {})


if __name__ == "__main__":
    unittest.main()
