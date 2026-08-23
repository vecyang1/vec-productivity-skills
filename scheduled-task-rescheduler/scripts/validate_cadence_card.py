#!/usr/bin/env python3
"""Validate cadence (scheduled-task) records in a Markdown file.

A cadence record is a Markdown card shaped like:

    ### `CAD-YYYYMMDD-slug` - Human Name

    | Field | Value |
    |---|---|
    | Status | `active` |
    | Execution Mode | `incremental` |
    | ...

This validator checks, for every card it finds:
  * required fields are present and non-empty,
  * status-style fields use the allowed vocabulary,
  * incremental records carry checkpoint / success / resume / stop fields,
  * `Root Alias` matches the alias used at the start of `Execution Root`.

It is intentionally dependency-free (Python 3 standard library only) so it can
run inside any pre-commit or pre-claim gate.

Exit codes: 0 = clean, 1 = validation errors (or warnings under --strict),
2 = usage error (no file / no cards).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_FIELDS = [
    "Status",
    "Activation Status",
    "Activation Mode",
    "Created",
    "Updated",
    "Created By",
    "Execution Root",
    "Root Alias",
    "Primary Runtime",
    "Schedule Frequency",
    "Timezone",
    "Catch Up Policy",
    "Retry Policy",
    "Execution Mode",
    "State Owner",
    "Output Owner",
    "Side Effect Level",
    "Source Refs",
]

# Required only when Execution Mode is "incremental".
INCREMENTAL_FIELDS = [
    "Checkpoint Path",
    "Success Marker Pattern",
    "Resume Policy",
    "Stop Condition",
]

VOCAB = {
    "Status": {
        "proposed", "planned", "active", "paused", "retired",
        "needs_prompt_recovery",
    },
    "Activation Status": {
        "designed", "awaiting_manual_paste", "active", "paused", "retired",
        "unknown_existing",
    },
    "Activation Mode": {
        "agent_self_schedule", "user_manual_paste", "external_runtime",
        "documented_only",
    },
    "Execution Mode": {"incremental", "full_rebuild", "audit_only"},
    "State Owner": {"project_local", "registry", "external_runtime", "none"},
    "Catch Up Policy": {
        "cheap_window_only", "catch_up_when_awake", "skip_if_stale",
        "manual_review",
    },
    "Retry Policy": {
        "retry_until_success", "retry_3_times", "no_retry", "manual_review",
    },
    "Side Effect Level": {
        "read_only", "writes_local", "writes_external", "publishes", "financial",
    },
}

CARD_RE = re.compile(r"^###\s+`(CAD-[A-Za-z0-9_\-]+)`\s*(?:[-–]\s*(.*))?$")
ROW_RE = re.compile(r"^\|(.+)\|(.+)\|\s*$")
ALIAS_RE = re.compile(r"^\{([A-Z0-9_]+)\}")


def strip_code(value: str) -> str:
    """Strip Markdown code-span backticks and surrounding whitespace."""
    return value.strip().strip("`").strip()


def is_separator(cell: str) -> bool:
    cell = cell.strip()
    return bool(cell) and set(cell) <= {"-", ":", " "}


def parse_cards(text: str):
    """Return a list of {id, name, fields:{}} for each cadence card."""
    cards = []
    current = None
    in_fence = False
    for raw in text.splitlines():
        line = raw.rstrip("\n")
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            # Toggle fenced-code state; never parse cards/rows inside a fence
            # (saved prompts and illustrative snippets live in code blocks).
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = CARD_RE.match(line.strip())
        if heading:
            if current is not None:
                cards.append(current)
            current = {
                "id": heading.group(1),
                "name": (heading.group(2) or "").strip(),
                "fields": {},
            }
            continue
        if current is None:
            continue
        row = ROW_RE.match(line)
        if not row:
            continue
        key = row.group(1).strip()
        value = row.group(2).strip()
        if is_separator(key) or is_separator(value):
            continue
        if key.lower() == "field" and value.lower() in ("value", "required meaning"):
            continue
        # First occurrence wins; ignore stray pipe lines inside prompt blocks
        # by only recording plausible field names.
        if key and key not in current["fields"]:
            current["fields"][key] = value
    if current is not None:
        cards.append(current)
    return cards


def validate_card(card):
    errors = []
    warnings = []
    fields = card["fields"]

    for required in REQUIRED_FIELDS:
        if required not in fields or not strip_code(fields[required]):
            errors.append(f"missing required field: {required}")

    for field, allowed in VOCAB.items():
        if field in fields:
            value = strip_code(fields[field])
            if value and value not in allowed:
                errors.append(
                    f"{field}='{value}' is not in allowed vocabulary "
                    f"{sorted(allowed)}"
                )

    if strip_code(fields.get("Execution Mode", "")) == "incremental":
        for required in INCREMENTAL_FIELDS:
            if required not in fields or not strip_code(fields[required]):
                errors.append(
                    f"incremental record is missing: {required}"
                )

    execution_root = strip_code(fields.get("Execution Root", ""))
    root_alias = strip_code(fields.get("Root Alias", ""))
    alias_match = ALIAS_RE.match(execution_root)
    if alias_match and root_alias and alias_match.group(1) != root_alias:
        errors.append(
            f"Root Alias '{root_alias}' does not match the alias in "
            f"Execution Root '{{{alias_match.group(1)}}}'"
        )

    # Soft hints — surfaced as warnings only.
    refs = strip_code(fields.get("Source Refs", ""))
    if strip_code(fields.get("Status", "")) == "retired" and not refs:
        warnings.append("retired card has no Source Refs to trace its history")

    return errors, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate cadence/scheduled-task records in a Markdown file."
    )
    parser.add_argument(
        "path", help="Markdown file containing one or more cadence cards"
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="treat warnings as failures",
    )
    args = parser.parse_args(argv)

    path = Path(args.path)
    if not path.is_file():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2

    cards = parse_cards(path.read_text(encoding="utf-8"))
    if not cards:
        print(
            "No cadence cards found. Expected headings like "
            "'### `CAD-YYYYMMDD-slug` - Name'.",
            file=sys.stderr,
        )
        return 2

    total_errors = 0
    total_warnings = 0
    for card in cards:
        errors, warnings = validate_card(card)
        total_errors += len(errors)
        total_warnings += len(warnings)
        label = f"{card['id']} - {card['name']}".rstrip(" -")
        if errors or warnings:
            print(f"\n{label}")
            for error in errors:
                print(f"  ERROR: {error}")
            for warning in warnings:
                print(f"  WARN:  {warning}")
        else:
            print(f"OK    {label}")

    print(
        f"\n{len(cards)} card(s), {total_errors} error(s), "
        f"{total_warnings} warning(s)"
    )
    if total_errors or (args.strict and total_warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
