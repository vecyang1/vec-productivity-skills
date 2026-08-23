#!/usr/bin/env python3
"""Read only: verify a Zernio key and exact publish destinations."""

from __future__ import annotations

import argparse
import sys
from typing import Any
from urllib.parse import urlencode

from zernio_client import APIError, request_json


def extract_accounts(payload: dict[str, Any]) -> list[dict[str, Any]]:
    accounts = payload.get("accounts", payload.get("data", []))
    if isinstance(accounts, dict):
        accounts = accounts.get("accounts", [])
    return [account for account in accounts if isinstance(account, dict)] if isinstance(accounts, list) else []


def select_exact_accounts(accounts: list[dict[str, Any]], *, platforms: list[str], account_ids: list[str]) -> list[dict[str, Any]]:
    if len(platforms) != len(account_ids):
        raise ValueError("--platforms and --account-ids must have the same number of values")
    selected: list[dict[str, Any]] = []
    for platform, account_id in zip(platforms, account_ids, strict=True):
        match = next((account for account in accounts if account.get("_id") == account_id and account.get("platform") == platform), None)
        if match is None:
            raise ValueError(f"requested destination is unavailable: {platform}/{account_id}")
        selected.append(match)
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile-id", help="optional Zernio profile ID")
    parser.add_argument("--platforms", nargs="+", help="exact destination platform values")
    parser.add_argument("--account-ids", nargs="+", help="exact destination account IDs, paired with --platforms")
    parser.add_argument("--show-account-ids", action="store_true", help="print account IDs after a successful read")
    args = parser.parse_args()
    if bool(args.platforms) != bool(args.account_ids):
        parser.error("use --platforms and --account-ids together")
    query = f"?{urlencode({'profileId': args.profile_id})}" if args.profile_id else ""
    try:
        _, payload = request_json("GET", "/accounts", query=query)
        accounts = extract_accounts(payload)
        if args.platforms:
            selected = select_exact_accounts(accounts, platforms=args.platforms, account_ids=args.account_ids)
            print(f"PASS: {len(selected)} exact destination(s) are accessible")
        else:
            print(f"PASS: {len(accounts)} connected account(s) are accessible")
        if args.show_account_ids:
            for account in accounts:
                print(f"{account.get('platform', 'unknown')}\t{account.get('_id', 'unknown')}")
        return 0
    except (APIError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
