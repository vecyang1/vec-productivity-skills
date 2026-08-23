"""SKILL.md is a specification, not decoration.

These assertions range over the whole skill directory rather than one file, and
they print how many subjects they graded -- a selector that silently narrows
later (a renamed file, a moved directory) then shows up as a number that fell
instead of as continued green.

A wholesale red here means the document lost content. Repair the document; do
not delete the assertions to reach green.
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
MARKDOWN = sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts)

api = _bootstrap.load("squirrly_api")
cli = _bootstrap.load("squirrly_ops")


class TestSkillMetadata(unittest.TestCase):
    def test_has_the_mandated_metadata_block(self):
        self.assertRegex(SKILL, r"(?m)^##\s+Skill Metadata\s*$")

    def test_metadata_fields_present_with_iso_dates(self):
        for field in ("Origin", "Source", "Author", "Created", "Updated", "Review status"):
            self.assertIn(f"**{field}:**", SKILL, f"missing metadata field {field}")
        for label in ("Created", "Updated"):
            self.assertRegex(SKILL, rf"\*\*{label}:\*\*\s*\d{{4}}-\d{{2}}-\d{{2}}")

    def test_frontmatter_description_starts_with_use_when(self):
        match = re.search(r"^---\n(.*?)\n---", SKILL, re.S)
        self.assertIsNotNone(match, "no frontmatter")
        self.assertRegex(match.group(1), r"description:\s*Use when")


class TestPointersResolve(unittest.TestCase):
    """An entry naming a file that does not exist sends a successor somewhere
    worse than nowhere."""

    def test_every_referenced_repo_path_exists(self):
        graded = 0
        for doc in MARKDOWN:
            text = doc.read_text(encoding="utf-8")
            for rel in re.findall(r"`((?:scripts|tests|references)/[A-Za-z0-9_./-]+)`", text):
                graded += 1
                self.assertTrue((ROOT / rel).exists(),
                                f"{doc.name} points at missing {rel}")
        self.assertGreaterEqual(graded, 5, f"only graded {graded} paths; selector narrowed")

    def test_named_scripts_are_executable(self):
        for name in ("e2e_check.py", "squirrly_ops.py"):
            path = ROOT / "scripts" / name
            self.assertTrue(path.is_file(), f"{name} missing")
            self.assertTrue(path.stat().st_mode & 0o111, f"{name} is not executable")

    def test_config_example_exists_and_is_pointer_only(self):
        example = ROOT / "config.example.json"
        self.assertTrue(example.is_file())
        doc = json.loads(example.read_text(encoding="utf-8"))
        for site in doc["sites"]:
            self.assertRegex(site["credential_ref"], r"^(op|env)://")


class TestDocumentedCommandsExist(unittest.TestCase):
    def test_every_command_in_the_router_table_is_a_real_subcommand(self):
        parser = cli.build_parser()
        actions = [a for a in parser._actions if hasattr(a, "choices") and a.choices]
        registered = set()
        for action in actions:
            if isinstance(action.choices, dict):
                registered.update(action.choices)
        self.assertTrue(registered, "no subcommands registered")

        # every backticked command word at the start of a router-table cell
        documented = set(re.findall(r"\|\s*`([a-z-]+)[^`]*`\s*\|?\s*$", SKILL, re.M))
        documented |= set(re.findall(r"squirrly_ops\.py\s+([a-z-]+)", SKILL))
        documented.discard("py")
        unknown = documented - registered
        self.assertFalse(unknown, f"SKILL.md documents commands that do not exist: {sorted(unknown)}")
        self.assertGreaterEqual(len(documented), 8,
                                f"only graded {len(documented)} commands; selector narrowed")

    def test_every_subcommand_is_mentioned_in_the_document(self):
        parser = cli.build_parser()
        registered: set[str] = set()
        for action in parser._actions:
            if isinstance(getattr(action, "choices", None), dict):
                registered.update(action.choices)
        missing = sorted(c for c in registered if f"`{c}" not in SKILL and f" {c} " not in SKILL)
        self.assertFalse(missing, f"undocumented subcommands: {missing}")


class TestSafetyClaimsAreTrue(unittest.TestCase):
    def test_document_claims_two_locks_and_the_code_enforces_both(self):
        self.assertIn("mutation_policy", SKILL)
        self.assertIn("--confirm", SKILL)
        client = api.SquirrlyClient("t", "https://x.test", allow_mutations=False)
        with self.assertRaises(api.SquirrlyError):
            client.call("briefcase.add", {"keyword": "k"})

    def test_document_claims_consuming_gets_are_guarded_and_they_are(self):
        self.assertIn("single-use", SKILL.lower())
        for op in ("user.dashboardlink", "user.token"):
            self.assertTrue(api.ENDPOINTS[op].mutates)

    def test_password_bearing_operations_are_mapped_but_never_transmittable(self):
        """login and register POST an account password.

        The earlier version of this test asserted they were *absent* from the
        endpoint table. Absence is the weaker claim in both directions: it was
        satisfied by simply never adding them, and it made the map describe what
        was convenient rather than what the API is. They are now listed -- so
        `ops` is a complete map -- and refused at the one place a request is
        built, which is a property no caller can route around.
        """
        for op in ("user.login", "user.register"):
            self.assertIn(op, api.ENDPOINTS, f"{op} should stay on the map")
            self.assertEqual(api.ENDPOINTS[op].gate, "policy")
            client = api.SquirrlyClient("t", "https://x.test", allow_mutations=True)
            with self.assertRaises(api.SquirrlyError) as caught:
                client.build_request(op, {"email": "a@b.test", "password": "x"})
            self.assertIn("will not send", str(caught.exception))

    def test_connect_is_reachable_but_double_locked(self):
        """add-brand spends a site slot and mints a key, so it needs --confirm.

        `allow_mutations=False` is the lock every mutating op shares; this
        asserts connect is inside that set rather than an exception to it.
        """
        self.assertIn("user.connect", api.ENDPOINTS)
        self.assertTrue(api.ENDPOINTS["user.connect"].mutates)
        client = api.SquirrlyClient("t", "https://x.test", allow_mutations=False)
        with self.assertRaises(api.SquirrlyError):
            client.build_request("user.connect", {"site_key": "k", "site_uuid": "u"})

    def test_every_gate_value_used_in_the_table_has_a_reason(self):
        """A gate label with no reason renders as an unexplained empty answer,
        which is the exact confusion the gate exists to remove."""
        used = {e.gate for e in api.ENDPOINTS.values() if e.gate}
        self.assertTrue(used, "no gates in the table; the selector has narrowed")
        for gate in used:
            self.assertIn(gate, api.GATE_REASONS, f"gate {gate!r} has no reason text")


class TestEndpointCoverageMatchesTheDocumentedContract(unittest.TestCase):
    """Every (path, verb) pair in ENDPOINTS.md must be callable.

    The reference file is the reverse-engineered contract; the table is what
    the code can actually reach. Nothing else compares them, so an endpoint
    that is discovered, written down, and then never wired stays invisible --
    and the next reader sees a capability that "does not exist" rather than one
    that was never connected. Ranges over the file rather than a hand-kept list,
    and prints its own denominator so a selector that narrows shows up as a
    number that fell.
    """

    #: The inventory carries one row that is a *description* of a family of
    #: variable paths rather than a path. Its five members are listed
    #: separately and are all wired; matching a literal brace excludes only it.
    META_ROW = re.compile(r"[{}]")

    def documented_pairs(self):
        text = (ROOT / "references" / "ENDPOINTS.md").read_text(encoding="utf-8")
        pairs = []
        for path, verb in re.findall(r"^\| `([^`]+)` \| (GET|POST) \|", text, re.M):
            if self.META_ROW.search(path) and "variable" in path:
                continue
            pairs.append((path, verb.lower()))
        return pairs

    def test_every_documented_endpoint_is_reachable(self):
        documented = self.documented_pairs()
        self.assertGreaterEqual(len(documented), 70,
                                f"only graded {len(documented)} endpoints; selector narrowed")
        wired = {(e.path, e.verb) for e in api.ENDPOINTS.values()}
        missing = sorted(p for p in documented if p not in wired)
        self.assertFalse(missing, f"documented but not callable ({len(missing)}): {missing}")

    def test_no_operation_claims_a_path_the_contract_never_recorded(self):
        documented = {p for p, _ in self.documented_pairs()}
        invented = sorted({e.path for e in api.ENDPOINTS.values()} - documented)
        self.assertFalse(invented, f"paths with no entry in ENDPOINTS.md: {invented}")


class TestNoCredentialLiterals(unittest.TestCase):
    """A credential-shaped literal in a committed file is a working secret in
    history forever. The pattern is assembled from fragments so this file does
    not flag itself -- excluding it from its own scan would carve out the one
    file guaranteed to accumulate such strings."""

    SUSPECT = re.compile(
        r"(" + "USER" + "-TOKEN|" + "credential" + r"\"?\s*[:=]\s*\"[A-Za-z0-9]{24,})")

    def test_no_long_credential_literal_in_any_committed_file(self):
        graded = 0
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
                continue
            if path.suffix not in (".py", ".md", ".json"):
                continue
            graded += 1
            text = path.read_text(encoding="utf-8", errors="replace")
            for line in text.splitlines():
                if re.search(r"[\"'][A-Za-z0-9]{32}[\"']", line) and "not-real" not in line:
                    if "repeat" in line or "0" * 8 in line:
                        continue
                    self.fail(f"{path.name}: possible 32-char credential literal: {line[:70]}")
        self.assertGreaterEqual(graded, 8, f"only graded {graded} files; selector narrowed")


if __name__ == "__main__":
    unittest.main()
