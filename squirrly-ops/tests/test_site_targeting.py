"""Brand targeting must be explicit, or a command silently hits the wrong brand.

A Squirrly token is bound to a site by the USER-URL header, and the plan carries
five site slots. So the moment a second brand is registered, any command that
resolved a brand implicitly starts answering about -- or writing to -- whichever
one happened to be first. These tests pin the selector semantics and the
boundary that keeps a credential value out of any output.
"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

api = _bootstrap.load("squirrly_api")

TWO_BRANDS = json.dumps({
    "schema_version": 1,
    "sites": [
        {"site_id": "alpha", "site_url": "https://alpha.test",
         "credential_ref": "op://Vault/AAA/credential",
         "mutation_policy": {"allow_writes": False}},
        {"site_id": "beta", "site_url": "https://beta.test",
         "credential_ref": "op://Vault/BBB/credential",
         "mutation_policy": {"allow_writes": True}},
    ],
})


class TestSelection(unittest.TestCase):
    def registry(self, payload=TWO_BRANDS, name="two.json"):
        return api.Registry.load(_bootstrap.write_registry(payload, name))

    def test_no_selector_refuses_and_enumerates(self):
        with self.assertRaises(api.SquirrlyError) as ctx:
            self.registry().select(None)
        message = str(ctx.exception)
        self.assertIn("alpha", message)
        self.assertIn("beta", message)

    def test_unknown_selector_refuses_and_enumerates(self):
        with self.assertRaises(api.SquirrlyError) as ctx:
            self.registry().select("gamma")
        self.assertIn("alpha, beta", str(ctx.exception))

    def test_exact_id_selects_that_brand(self):
        self.assertEqual(self.registry().select("beta").site_url, "https://beta.test")

    def test_bare_host_selects_on_an_exact_match(self):
        self.assertEqual(self.registry().select("alpha.test").site_id, "alpha")

    def test_near_miss_does_not_fuzzy_match(self):
        """A typo must fail, not resolve to the closest brand."""
        for typo in ("alph", "Alpha", "alpha.test.", "https://alpha.test/x"):
            with self.assertRaises(api.SquirrlyError, msg=f"{typo!r} was accepted"):
                self.registry().select(typo)

    def test_single_brand_registry_still_requires_the_flag(self):
        """The dangerous moment is the day a second brand is added: a command
        that had been defaulting to 'the only one' keeps running and starts
        being ambiguous, with nothing to signal the change."""
        one = json.dumps({"sites": [
            {"site_id": "solo", "site_url": "https://solo.test",
             "credential_ref": "op://V/I/credential"}]})
        with self.assertRaises(api.SquirrlyError):
            self.registry(one, "one.json").select(None)


class TestRegistryValidation(unittest.TestCase):
    def load(self, doc, name):
        return api.Registry.load(_bootstrap.write_registry(json.dumps(doc), name))

    def test_missing_credential_ref_is_rejected_at_load(self):
        with self.assertRaises(api.SquirrlyError) as ctx:
            self.load({"sites": [{"site_id": "a", "site_url": "https://a.test"}]}, "bad1.json")
        self.assertIn("credential_ref", str(ctx.exception))

    def test_duplicate_site_id_is_rejected(self):
        doc = {"sites": [
            {"site_id": "dup", "site_url": "https://a.test", "credential_ref": "op://V/I/c"},
            {"site_id": "dup", "site_url": "https://b.test", "credential_ref": "op://V/J/c"},
        ]}
        with self.assertRaises(api.SquirrlyError) as ctx:
            self.load(doc, "bad2.json")
        self.assertIn("duplicate", str(ctx.exception).lower())

    def test_missing_file_explains_how_to_create_one(self):
        with self.assertRaises(api.SquirrlyError) as ctx:
            api.Registry.load(str(_bootstrap.SANDBOX / "nope.json"))
        self.assertIn("config.example.json", str(ctx.exception))

    def test_malformed_json_names_the_file(self):
        path = _bootstrap.write_registry("{not json", "broken.json")
        with self.assertRaises(api.SquirrlyError) as ctx:
            api.Registry.load(path)
        self.assertIn("broken.json", str(ctx.exception))


class TestWritePolicy(unittest.TestCase):
    def test_write_needs_the_registry_to_allow_it(self):
        registry = api.Registry.load(_bootstrap.write_registry(TWO_BRANDS, "pol.json"))
        self.assertFalse(registry.select("alpha").may_write())
        self.assertTrue(registry.select("beta").may_write())

    def test_absent_policy_defaults_to_no_writes(self):
        doc = json.dumps({"sites": [
            {"site_id": "x", "site_url": "https://x.test", "credential_ref": "op://V/I/c"}]})
        registry = api.Registry.load(_bootstrap.write_registry(doc, "nopol.json"))
        self.assertFalse(registry.select("x").may_write(),
                         "a brand with no stated policy must not be writable")


class TestSecretBoundary(unittest.TestCase):
    def test_registry_holds_a_pointer_not_a_value(self):
        registry = api.Registry.load(_bootstrap.write_registry(TWO_BRANDS, "sec.json"))
        for site in registry.sites.values():
            self.assertTrue(site.credential_ref.startswith(("op://", "env://")))

    def test_the_real_registry_is_never_touched_by_the_suite(self):
        """The sandbox must be structural, not a mock someone has to remember."""
        import os
        self.assertTrue(os.environ["SQUIRRLY_OPS_CONFIG"].startswith(str(_bootstrap.SANDBOX)))
        self.assertNotEqual(Path(os.environ["SQUIRRLY_OPS_CONFIG"]), _bootstrap.REAL_CONFIG)

    def test_client_never_exposes_the_token_as_an_attribute_or_repr(self):
        client = api.SquirrlyClient("super-secret-value", "https://a.test")
        self.assertNotIn("super-secret-value", repr(client))
        self.assertFalse(hasattr(client, "token"),
                         "a public .token attribute invites it into a log line")


if __name__ == "__main__":
    unittest.main()
