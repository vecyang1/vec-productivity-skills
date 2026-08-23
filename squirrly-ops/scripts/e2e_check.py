#!/usr/bin/env python3
"""Prove a squirrly-ops setup works end to end, against the real API.

What this checks that the unit suite structurally cannot:

* the 1Password Service Account bridge is running and resolves the pointer
  without an interactive prompt -- the unit suite asserts the personal route is
  *refused*, which says nothing about the unattended route working;
* the resolved token authenticates against the live API for the registered
  USER-URL;
* the endpoint verbs in the table match what the server currently accepts;
* the brand guard refuses an unknown site.

Redacted receipt: stage outcomes, counts and shapes only -- never a token, never
a dashboard URL, never a response body. Exit 0 only when every stage passes.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from squirrly_api import Registry, SquirrlyClient, SquirrlyError, resolve_credential  # noqa: E402

DEFAULT_SINK = Path.home() / ".cache" / "squirrly-ops-e2e" / "e2e.out"


class Receipt:
    def __init__(self) -> None:
        self.stages: list[dict] = []

    def record(self, name: str, fn) -> object:
        started = time.monotonic()
        try:
            detail = fn()
            self.stages.append({"stage": name, "result": "pass", "detail": detail,
                                "ms": round((time.monotonic() - started) * 1000)})
            return detail
        except Exception as exc:  # noqa: BLE001 - every failure is a stage result
            self.stages.append({"stage": name, "result": "FAIL",
                                "detail": f"{type(exc).__name__}: {exc}",
                                "ms": round((time.monotonic() - started) * 1000)})
            return None

    @property
    def ok(self) -> bool:
        return bool(self.stages) and all(s["result"] == "pass" for s in self.stages)


def run(site_id: str | None, config: str | None) -> Receipt:
    receipt = Receipt()
    state: dict = {}

    def load_registry():
        registry = Registry.load(config)
        state["registry"] = registry
        return {"config": str(registry.path), "brands": sorted(registry.sites)}

    def select_brand():
        registry = state["registry"]
        chosen = site_id or next(iter(sorted(registry.sites)), None)
        if chosen is None:
            raise SquirrlyError("registry defines no brands")
        site = registry.select(chosen)
        state["site"] = site
        return {"site_id": site.site_id, "url": site.site_url,
                "writes": "allowed" if site.may_write() else "blocked"}

    def guard_rejects_unknown_brand():
        try:
            state["registry"].select("definitely-not-a-configured-brand")
        except SquirrlyError as exc:
            return {"refused": True, "enumerates": "Configured brands" in str(exc)}
        raise AssertionError("an unknown brand was accepted")

    def resolve_token():
        site = state["site"]
        token = resolve_credential(site.credential_ref)
        site_key = resolve_credential(site.site_key_ref) if site.site_key_ref else ""
        state["client"] = SquirrlyClient(token, site.site_url, site_key=site_key,
                                         blog_id=site.blog_id, origin=site.origin)
        # lengths and schemes only: never a value, never a prefix of one
        return {"resolved": True, "token_length": len(token),
                "site_key_length": len(site_key),
                "scheme": site.credential_ref.split("://")[0]}

    def signing_is_configured_when_the_brand_needs_it():
        """A brand with a blog id MUST sign; the server answers 403
        `signature_required` otherwise, and that message is identical to the one
        a bad token produces. Without this stage a silent regression to unsigned
        auth would only surface as a confusing auth failure in production."""
        site = state["site"]
        if not site.blog_id:
            return {"signed_auth": "not required for this brand"}
        _, request = state["client"].build_request("user.stats")
        headers = {k.lower() for k in dict(request.header_items())}
        missing = [h for h in ("x-sq-sig", "x-sq-blog-id", "x-sq-nonce",
                               "x-sq-timestamp") if h not in headers]
        if missing:
            raise AssertionError(f"brand has blog_id but request is unsigned: missing {missing}")
        return {"signed_auth": "active", "blog_id": site.blog_id}

    def authenticate():
        data = state["client"].call("user.checkin") or {}
        if not data:
            raise SquirrlyError("checkin returned no data")
        return {"status": data.get("subscription_status"),
                "product": data.get("product_name"),
                "site_slots": data.get("subscription_max_blogs")}

    def read_get_endpoint():
        data = state["client"].call("briefcase.get") or {}
        return {"keywords": len(data.get("keywords", [])),
                "server_total": state["client"].last_total}

    def read_list_endpoint():
        rows, total = state["client"].paginate("kr.found", page_size=50)
        return {"rows": len(rows), "server_total": total,
                "reconciles": (total is None) or len(rows) >= min(total, 50)}

    def verb_table_matches_server():
        """A 405 here means the pinned verb no longer matches the server."""
        state["client"].call("audits.notifications")
        return {"checked": "audits.notifications", "status": "accepted"}

    def write_is_blocked_by_default():
        try:
            state["client"].call("briefcase.add", {"keyword": "e2e-should-never-send"})
        except SquirrlyError as exc:
            if "--confirm" not in str(exc):
                raise
            return {"refused": True}
        raise AssertionError("a mutating call was sent without --confirm")

    receipt.record("load registry", load_registry)
    if receipt.ok:
        receipt.record("select brand", select_brand)
    if receipt.ok:
        receipt.record("guard refuses unknown brand", guard_rejects_unknown_brand)
        receipt.record("resolve credential (unattended)", resolve_token)
    if receipt.ok:
        receipt.record("signing configured for this brand",
                       signing_is_configured_when_the_brand_needs_it)
        receipt.record("authenticate live", authenticate)
        receipt.record("read GET endpoint", read_get_endpoint)
        receipt.record("read paginated endpoint", read_list_endpoint)
        receipt.record("verb table matches server", verb_table_matches_server)
        receipt.record("write blocked without --confirm", write_is_blocked_by_default)
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="End-to-end check for squirrly-ops.")
    parser.add_argument("--site", help="brand id (default: first in the registry)")
    parser.add_argument("--config", help="registry path")
    parser.add_argument("--sink", default=os.environ.get("SQUIRRLY_E2E_SINK", str(DEFAULT_SINK)))
    args = parser.parse_args(argv)

    receipt = run(args.site, args.config)
    payload = {"ok": receipt.ok, "stages": receipt.stages}
    rendered = json.dumps(payload, indent=2, default=str)

    sink = Path(args.sink).expanduser()
    sink.parent.mkdir(parents=True, exist_ok=True)
    sink.write_text(rendered, encoding="utf-8")

    # The 1Password fixed-command adapter discards child stdout, so the receipt
    # on disk is the durable artefact; stdout is a convenience for humans.
    print(rendered)
    print(f"\nreceipt: {sink}", file=sys.stderr)
    for stage in receipt.stages:
        if stage["result"] != "pass":
            print(f"FAILED at: {stage['stage']} -> {stage['detail']}", file=sys.stderr)
    return 0 if receipt.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
