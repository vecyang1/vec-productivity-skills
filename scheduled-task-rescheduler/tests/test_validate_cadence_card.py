#!/usr/bin/env python3
"""Tests for validate_cadence_card.py — Python stdlib unittest, no dependencies.

Run from anywhere:

    python3 -m unittest discover -s scheduled-task-rescheduler/tests

or directly:

    python3 scheduled-task-rescheduler/tests/test_validate_cadence_card.py
"""
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import validate_cadence_card as v  # noqa: E402

VALID_CARD = """\
### `CAD-20260101-x` - Example

| Field | Value |
|---|---|
| Status | `active` |
| Activation Status | `active` |
| Activation Mode | `external_runtime` |
| Created | `2026-01-01` |
| Updated | `2026-01-01` |
| Created By | `You` |
| Execution Root | `{PROJECT_ROOT}` |
| Root Alias | `PROJECT_ROOT` |
| Primary Runtime | `cron` |
| Schedule Frequency | `daily` |
| Timezone | `Asia/Bangkok` |
| Catch Up Policy | `cheap_window_only` |
| Retry Policy | `no_retry` |
| Execution Mode | `full_rebuild` |
| State Owner | `none` |
| Output Owner | `reports/x.md` |
| Side Effect Level | `writes_local` |
| Source Refs | `none` |
"""


class TestParsing(unittest.TestCase):
    def test_valid_card_has_no_errors(self):
        cards = v.parse_cards(VALID_CARD)
        self.assertEqual(len(cards), 1)
        errors, _ = v.validate_card(cards[0])
        self.assertEqual(errors, [], f"unexpected errors: {errors}")

    def test_card_inside_code_fence_is_ignored(self):
        # Regression guard: a `### \`CAD-...\`` heading inside a fenced code
        # block (e.g. an illustrative snippet or a saved prompt) must NOT be
        # parsed as a live card.
        fenced = "```markdown\n" + VALID_CARD + "```\n"
        self.assertEqual(v.parse_cards(fenced), [])

    def test_missing_required_fields_reported(self):
        cards = v.parse_cards(
            "### `CAD-1-y` - Y\n\n| Field | Value |\n|---|---|\n| Status | `active` |\n"
        )
        errors, _ = v.validate_card(cards[0])
        self.assertTrue(any("missing required field" in e for e in errors))


class TestValidationRules(unittest.TestCase):
    def test_bad_vocabulary_reported(self):
        card = {"id": "CAD-1-z", "name": "Z", "fields": {"Status": "`banana`"}}
        errors, _ = v.validate_card(card)
        self.assertTrue(any("not in allowed vocabulary" in e for e in errors))

    def test_incremental_requires_state_fields(self):
        text = VALID_CARD.replace("`full_rebuild`", "`incremental`")
        cards = v.parse_cards(text)
        errors, _ = v.validate_card(cards[0])
        self.assertTrue(any("incremental record is missing" in e for e in errors))

    def test_alias_mismatch_reported(self):
        text = VALID_CARD.replace(
            "| Root Alias | `PROJECT_ROOT` |", "| Root Alias | `WRONG` |"
        )
        cards = v.parse_cards(text)
        errors, _ = v.validate_card(cards[0])
        self.assertTrue(any("does not match the alias" in e for e in errors))


class TestShippedTemplate(unittest.TestCase):
    def _template(self):
        return SKILL_ROOT / "references" / "cadence-card-template.md"

    def test_template_exposes_one_clean_card(self):
        cards = v.parse_cards(self._template().read_text(encoding="utf-8"))
        self.assertEqual(len(cards), 1, "template should expose exactly one live card")
        errors, _ = v.validate_card(cards[0])
        self.assertEqual(errors, [], f"template card has errors: {errors}")

    def test_main_returns_zero_on_template(self):
        self.assertEqual(v.main([str(self._template()), "--strict"]), 0)


if __name__ == "__main__":
    unittest.main()
