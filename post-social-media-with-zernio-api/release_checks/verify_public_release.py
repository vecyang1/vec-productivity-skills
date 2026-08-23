#!/usr/bin/env python3
"""Fail closed when a community Zernio skill contains private release material."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


SKIP_DIRECTORIES = {".git", "__pycache__", ".pytest_cache", "graphify-out"}
PLACEHOLDER_EMAIL_DOMAINS = {"example.com", "example.org", "example.net", "invalid.test"}
PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("live Zernio credential", re.compile(r"(?<![A-Za-z0-9_])sk_[0-9a-fA-F]{64}(?![A-Za-z0-9_])")),
    ("local-machine path", re.compile(r"/" r"Users/[^\s\"'`<>]+")),
    ("non-example email", re.compile(r"(?<![\w.-])[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})(?![\w.-])")),
    ("concrete Zernio identifier", re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]{24}(?![0-9a-fA-F])")),
)


@dataclass(frozen=True)
class Finding:
    category: str
    path: str


def is_placeholder_email(match: re.Match[str]) -> bool:
    return match.group(1).lower() in PLACEHOLDER_EMAIL_DOMAINS


def scan_text(text: str, path: str) -> list[Finding]:
    findings: list[Finding] = []
    for category, pattern in PATTERNS:
        for match in pattern.finditer(text):
            if category == "non-example email" and is_placeholder_email(match):
                continue
            findings.append(Finding(category=category, path=path))
            break
    return findings


def iter_files(root: Path):
    for candidate in root.rglob("*"):
        if any(part in SKIP_DIRECTORIES for part in candidate.parts):
            continue
        if candidate.is_file():
            yield candidate


def scan_working_tree(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for candidate in iter_files(root):
        try:
            text = candidate.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        findings.extend(scan_text(text, candidate.relative_to(root).as_posix()))
    return findings


def git_output(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.DEVNULL)


def scan_reachable_history(root: Path) -> list[Finding]:
    git_root = Path(git_output(root, "rev-parse", "--show-toplevel").decode().strip())
    package_path = root.resolve().relative_to(git_root.resolve()).as_posix()
    revisions = git_output(git_root, "rev-list", "--all").decode().splitlines()
    findings: list[Finding] = []
    for revision in revisions:
        tree = git_output(git_root, "ls-tree", "-r", "--name-only", revision, "--", package_path).decode().splitlines()
        for tracked_path in tree:
            relative_path = Path(tracked_path).relative_to(package_path)
            if any(part in SKIP_DIRECTORIES for part in relative_path.parts):
                continue
            try:
                text = git_output(git_root, "show", f"{revision}:{tracked_path}").decode("utf-8")
            except UnicodeDecodeError:
                continue
            findings.extend(scan_text(text, relative_path.as_posix()))
    return findings


def report(scope: str, findings: list[Finding]) -> None:
    if not findings:
        print(f"PASS: {scope}")
        return
    print(f"FAIL: {scope} has {len(findings)} privacy finding(s)")
    for finding in findings:
        print(f"- {finding.category}: {finding.path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history", action="store_true", help="also scan all reachable Git revisions")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    findings = scan_working_tree(root)
    report("working tree", findings)
    if args.history:
        history_findings = scan_reachable_history(root)
        report("reachable history", history_findings)
        findings.extend(history_findings)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
