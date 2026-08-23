#!/usr/bin/env python3
"""squirrly-ops - multi-brand CLI for the Squirrly SEO cloud API.

    python3 squirrly_ops.py sites
    python3 squirrly_ops.py --site <brand> doctor
    python3 squirrly_ops.py --site <brand> checks

Every command that touches an account requires an explicit ``--site``. The
resolved target is echoed to stderr before any request, so a run that is about
to talk to the wrong brand says so in its first line.

Secrets never reach stdout. That includes URLs: ``dashboard`` mints a one-shot
auto-login link, so it opens the browser by default and only prints with an
explicit opt-in.
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import subprocess
import sys
import uuid
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from squirrly_api import (  # noqa: E402
    ENDPOINTS,
    GATE_REASONS,
    ONEPASSWORD_SCRIPTS,
    Registry,
    Site,
    SquirrlyClient,
    SquirrlyError,
    decode_embedded_json,
    resolve_credential,
)

UNKNOWN = "unknown"


# --------------------------------------------------------------------------
# output helpers
# --------------------------------------------------------------------------

def emit(payload: Any, fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
        return
    _table(payload)


def _table(payload: Any, indent: int = 0) -> None:
    pad = "  " * indent
    if isinstance(payload, dict):
        width = max((len(str(k)) for k in payload), default=0)
        for key, value in payload.items():
            if isinstance(value, (dict, list)) and value:
                print(f"{pad}{key}:")
                _table(value, indent + 1)
            else:
                shown = "-" if value in (None, "", [], {}) else value
                print(f"{pad}{str(key):<{width}}  {shown}")
    elif isinstance(payload, list):
        if not payload:
            print(f"{pad}(none)")
        for item in payload:
            if isinstance(item, dict):
                _table(item, indent)
                print()
            else:
                print(f"{pad}- {item}")
    else:
        print(f"{pad}{payload}")


def warn(message: str) -> None:
    """Warnings go to stderr so --output json stays a clean pipe."""
    print(f"[squirrly-ops] {message}", file=sys.stderr)


def _num(source: dict[str, Any], key: str) -> Any:
    """Read a numeric field, distinguishing absent from zero.

    A missing quota field must not render as 0 -- "0 researches left" and "the
    API stopped sending this field" are opposite facts and only one of them
    should stop someone from working.
    """
    if key not in source or source[key] is None:
        return UNKNOWN
    return source[key]


# --------------------------------------------------------------------------
# connection
# --------------------------------------------------------------------------

def connect(args: argparse.Namespace) -> tuple[Site, SquirrlyClient]:
    registry = Registry.load(args.config)
    site = registry.select(args.site)
    warn(f"target: {site.site_url} (site={site.site_id})")

    allow = bool(getattr(args, "confirm", False))
    if allow and not site.may_write():
        raise SquirrlyError(
            f"--confirm was passed but {site.site_id} has "
            "mutation_policy.allow_writes = false in the registry. "
            "A write needs both: the flag proves intent, the registry proves the "
            "brand is meant to be writable at all."
        )
    token = resolve_credential(site.credential_ref)
    # A brand that has completed its plugin handshake gets a blog id, and the
    # server then rejects every unsigned call with 403 `signature_required`.
    # Both parts are required together, so refuse a half-configured brand rather
    # than sending an unsigned request that fails with a misleading auth error.
    site_key = ""
    if site.site_key_ref or site.blog_id:
        if not (site.site_key_ref and site.blog_id):
            raise SquirrlyError(
                f"{site.site_id} has only one half of its signing config: "
                f"site_key_ref={'set' if site.site_key_ref else 'missing'}, "
                f"blog_id={'set' if site.blog_id else 'missing'}. "
                "Signed auth needs both; with one the server answers 403 "
                "signature_required, which reads like a bad token."
            )
        site_key = resolve_credential(site.site_key_ref)
    return site, SquirrlyClient(token, site.site_url, allow_mutations=allow,
                                site_key=site_key, blog_id=site.blog_id,
                                origin=site.origin)


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------

def cmd_sites(args: argparse.Namespace) -> int:
    registry = Registry.load(args.config)
    rows = [
        {
            "site_id": s.site_id,
            "site_url": s.site_url,
            "label": s.label or "-",
            "credential": s.credential_ref.split("/")[-2] if s.credential_ref.startswith("op://") else s.credential_ref,
            "writes": "allowed" if s.may_write() else "blocked",
            "notes": s.notes or "-",
        }
        for s in sorted(registry.sites.values(), key=lambda x: x.site_id)
    ]
    emit({"config": str(registry.path), "count": len(rows), "sites": rows}, args.output)
    return 0


def cmd_ops(args: argparse.Namespace) -> int:
    """List the whole endpoint map, including what this account cannot use.

    Endpoints an account is not entitled to are kept and labelled rather than
    dropped. Dropping them would make the map describe one subscription instead
    of the API, and an endpoint that is missing is indistinguishable from one
    that does not exist -- which is how a later reader concludes a capability
    is absent when it is merely unpaid for here.
    """
    selected = sorted(ENDPOINTS.values(), key=lambda x: x.op)
    if args.gate:
        selected = [e for e in selected if e.gate == args.gate]
    rows = [
        {"op": e.op, "verb": e.verb.upper(), "path": e.path,
         "mutates": e.mutates, "required": ", ".join(e.required) or "-",
         "gate": e.gate or "-",
         "gate_reason": GATE_REASONS.get(e.gate, "") if e.gate else "",
         "note": e.note}
        for e in selected
    ]
    counts: dict[str, int] = {}
    for endpoint in ENDPOINTS.values():
        counts[endpoint.gate or "open"] = counts.get(endpoint.gate or "open", 0) + 1
    emit({"count": len(rows), "by_gate": counts, "operations": rows}, args.output)
    return 0


def _plan_payload(checkin: dict[str, Any], *, configured_locally: Any = UNKNOWN) -> dict[str, Any]:
    """Shape the raw checkin into a plan+quota view.

    The `subscription_<resource>` counters are REMAINING, not used. Proven from
    the vendor plugin's own UI (view/Blocks/Account.php renders '%1$s of %2$s
    left' with the counter as the first slot, and its tooltip computes
    used = max - counter). Getting this backwards inverts every number here.

    Site slots are the one number the Cloud will not answer. `user.checkin`
    reports `subscription_max_blogs` and nothing that counts the blogs already
    registered, so `used` here is *unknown* and only the local registry can say
    how many this machine is configured for. Those are different questions --
    a blog connected from another machine is invisible to both -- so they are
    reported as separate fields rather than one number that would read as an
    account fact. An earlier version of this function returned a hardcoded
    `used_here: 1`, which was correct exactly once and could never have gone
    wrong out loud.
    """
    def quota(name: str, label: str) -> dict[str, Any]:
        left = _num(checkin, f"subscription_{name}")
        cap = _num(checkin, f"subscription_max_{name}")
        used: Any = UNKNOWN
        if isinstance(left, (int, float)) and isinstance(cap, (int, float)):
            used = max(0, int(cap) - int(left))
        return {"resource": label, "left": left, "of": cap, "used": used}

    return {
        "product": checkin.get("product_name", UNKNOWN),
        "type": checkin.get("product_type", UNKNOWN),
        "status": checkin.get("subscription_status", UNKNOWN),
        "one_time": bool(checkin.get("subscription_onetime")),
        "expires": checkin.get("subscription_expires") or "never",
        "limits_reset": checkin.get("subscription_limits_reset", UNKNOWN),
        "site_slots": {
            "max": _num(checkin, "subscription_max_blogs"),
            "used_on_account": UNKNOWN,
            "configured_locally": configured_locally,
        },
        "connections": {
            "search_console": bool(checkin.get("connection_gsc")),
            "analytics": bool(checkin.get("connection_ga")),
        },
        "quota": [
            quota("kr", "keyword research"),
            quota("audit_pages", "audit pages"),
            quota("focus_pages", "focus pages"),
            quota("serps", "SERP rank checks"),
        ],
    }


def cmd_plan(args: argparse.Namespace) -> int:
    site, client = connect(args)
    registry = Registry.load(args.config)
    checkin = client.call("user.checkin")
    if not isinstance(checkin, dict):
        raise SquirrlyError("user.checkin did not return an object.")
    payload = _plan_payload(checkin, configured_locally=len(registry.sites))
    for row in payload["quota"]:
        if row["left"] == 0 and row["of"] == 0:
            warn(f"{row['resource']}: not included in this plan (0 of 0).")
    emit(payload, args.output)
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    site, client = connect(args)
    stages: list[dict[str, Any]] = []
    ok = True

    def stage(name: str, fn) -> Any:
        nonlocal ok
        try:
            value = fn()
            stages.append({"stage": name, "result": "pass", "detail": value})
            return value
        except SquirrlyError as exc:
            ok = False
            stages.append({"stage": name, "result": "FAIL", "detail": str(exc)})
            return None

    # One checkin call, reused. Re-fetching per stage would spend two round
    # trips to answer one question and could report two different states.
    account: dict[str, Any] = {}

    def authenticate() -> dict[str, Any]:
        account.update(client.call("user.checkin") or {})
        if not account:
            raise SquirrlyError("user.checkin returned nothing")
        return {"connected": bool(account.get("connected"))}

    checkin = stage("authenticate", authenticate)
    stage("account", lambda: {
        "product": account.get("product_name", UNKNOWN),
        "status": account.get("subscription_status", UNKNOWN),
        "site_slots": _num(account, "subscription_max_blogs"),
    })
    stage("read briefcase", lambda: {"keywords": len((client.call("briefcase.get") or {}).get("keywords", []))})
    stage("read checks", lambda: {"checks": len(client.call("audits.notifications") or {})})

    verdict = "ok" if ok and checkin else "FAILED"
    emit({"site": site.site_id, "url": site.site_url, "verdict": verdict, "stages": stages}, args.output)
    return 0 if verdict == "ok" else 1


def cmd_checks(args: argparse.Namespace) -> int:
    _, client = connect(args)
    raw = client.call("audits.notifications")
    if not isinstance(raw, dict):
        raise SquirrlyError("audits.notifications did not return an object.")
    rows = []
    for name, item in raw.items():
        if not isinstance(item, dict):
            continue
        done = item.get("completed")
        # The server sends printf templates ("You ranked on %s with %s"); the
        # plugin substitutes them from local WordPress state we do not have.
        # An unsubstituted template is not a message, so it is dropped rather
        # than shown as if it said something.
        hint = item.get("warning") or item.get("solution") or ""
        if "%s" in hint or "%1$s" in hint:
            hint = ""
        rows.append({
            "check": name,
            "status": "pass" if done is True else ("todo" if done is False else UNKNOWN),
            "hint": hint,
        })
    rows.sort(key=lambda r: (r["status"] != "todo", r["check"]))
    todo = [r for r in rows if r["status"] == "todo"]
    if args.todo:
        rows = todo
    emit({"total": len(raw), "outstanding": len(todo), "checks": rows}, args.output)
    return 0


def cmd_keywords(args: argparse.Namespace) -> int:
    _, client = connect(args)
    data = client.call("briefcase.get") or {}
    # Capture before the next call: last_total belongs to the most recent
    # request, so reading it after briefcase.stats would report the wrong total.
    briefcase_total = client.last_total
    stats = client.call("briefcase.stats") or {}
    keywords = []
    for kw in data.get("keywords", []) or []:
        keywords.append({
            "id": kw.get("id"),
            "keyword": kw.get("keyword"),
            "score": kw.get("score"),
            "rank": kw.get("rank"),
            "searches": kw.get("search"),
            "posts": len(kw.get("posts") or []),
            "labels": [l.get("name", l) if isinstance(l, dict) else l for l in (kw.get("labels") or [])],
            "research": decode_embedded_json(kw.get("research")),
        })
    emit({
        "stats": stats,
        "count": len(keywords),
        "server_total": briefcase_total if briefcase_total is not None else UNKNOWN,
        "keywords": keywords,
    }, args.output)
    return 0


def cmd_research(args: argparse.Namespace) -> int:
    _, client = connect(args)
    if args.all:
        found, total = client.paginate("kr.found")
    else:
        found = client.call("kr.found") or []
        total = client.last_total
    rows = []
    for item in found if isinstance(found, list) else []:
        detail = decode_embedded_json(item.get("data")) or {}
        rank = detail.get("rank") if isinstance(detail, dict) else {}
        rows.append({
            "id": item.get("id"),
            "keyword": item.get("keyword"),
            "country": item.get("country"),
            "opportunity": (rank or {}).get("text") if isinstance(rank, dict) else UNKNOWN,
            "score": (rank or {}).get("value") if isinstance(rank, dict) else UNKNOWN,
            "in_briefcase": item.get("in_briefcase"),
            "found_at": item.get("datetime"),
        })
    fetched = len(rows)
    if args.keyword:
        needle = args.keyword.lower()
        rows = [r for r in rows if needle in (r["keyword"] or "").lower()]
    # Reconcile against the server's own count so a truncated read cannot be
    # mistaken for a complete one. `total` is None when the server did not say.
    if isinstance(total, int) and fetched < total:
        warn(f"showing {fetched} of {total} stored results - pass --all to page through them.")
    emit({
        "fetched": fetched,
        "server_total": total if total is not None else UNKNOWN,
        "shown": len(rows),
        "research": rows,
    }, args.output)
    return 0


def cmd_focus(args: argparse.Namespace) -> int:
    _, client = connect(args)
    audits = client.call("audits.focus") or []
    rows = []
    for item in audits if isinstance(audits, list) else []:
        detail = decode_embedded_json(item.get("audit")) or {}
        props = detail.get("properties", {}) if isinstance(detail, dict) else {}
        rows.append({
            "post_id": item.get("user_post_id"),
            "url": item.get("permalink"),
            "indexed": item.get("indexed"),
            "visible": item.get("visibility"),
            "crawled": props.get("successCrawl") if isinstance(props, dict) else UNKNOWN,
            "checked_at": props.get("created_at") if isinstance(props, dict) else UNKNOWN,
        })
    payload: dict[str, Any] = {"count": len(rows), "focus_pages": rows}
    if args.full:
        payload["raw"] = [decode_embedded_json(i.get("audit")) for i in audits] if isinstance(audits, list) else audits
    emit(payload, args.output)
    return 0


def cmd_ai_visibility(args: argparse.Namespace) -> int:
    _, client = connect(args)
    data = client.call("audits.ai_visibility") or {}
    if isinstance(data, dict) and not data.get("total_visits"):
        warn("total_visits is 0 - this metric is derived from the connected "
             "Analytics property, so 0 can mean 'no AI referrals' or 'no data "
             "reaching Squirrly yet'. It does not distinguish them.")
    emit(data, args.output)
    return 0


def cmd_dashboard(args: argparse.Namespace) -> int:
    _, client = connect(args)
    # dashboardlink is marked mutating because it consumes a single-use link.
    # Minting one is this command's entire purpose, so the command itself is the
    # consent -- unlike `raw user.dashboardlink`, which still needs --confirm.
    client.allow_mutations = True
    data = client.call("user.dashboardlink") or {}
    url = data.get("url")
    if not url:
        raise SquirrlyError("no dashboard URL returned.")
    if args.print_url:
        warn("printing a ONE-SHOT auto-login link to stdout. It authenticates "
             "this Squirrly account on first use. Do not paste it anywhere.")
        emit({"url": url, "blog_id": data.get("blog_id"), "single_use": True}, args.output)
        return 0
    subprocess.run(["open", url], check=False)
    emit({"opened": True, "blog_id": data.get("blog_id"),
          "note": "one-shot login link handed to the browser; not printed"}, args.output)
    return 0


INSPIRE_SOURCES = {"blog": "inspire.blog", "wiki": "inspire.wiki",
                   "twitter": "inspire.twitter", "images": "inspire.images"}


def cmd_inspire(args: argparse.Namespace) -> int:
    """Third-party research for a topic, via Squirrly's Inspiration Box proxy."""
    _, client = connect(args)
    sources = [args.source] if args.source else sorted(INSPIRE_SOURCES)
    results: dict[str, Any] = {}
    for name in sources:
        try:
            payload = client.call(INSPIRE_SOURCES[name], {"q": args.query})
        except SquirrlyError as exc:
            # One dead source must not lose the other three.
            results[name] = {"error": str(exc)}
            continue
        if isinstance(payload, dict):
            payload = payload.get("results") or payload.get("responseData") or payload
        results[name] = payload
    emit({"query": args.query, "sources": results}, args.output)
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    """The site audit: an overall score plus the tasks that are not complete.

    Two prerequisites are invisible from the endpoint alone and both answer with
    an empty list rather than an error, which reads as "nothing wrong":

    * `days_back` must be sent. The vendor's own caller sends 30.
    * The audit only exists once at least one page is registered AND crawled.
      A blog with no audit pages returns `[]` forever.

    `--crawl <url>` does both halves: `posts.set_audit` registers the permalink
    and hands back a user_post_id, then `posts.crawl` needs BOTH that id and the
    url -- sending only the url answers `The post id field is required`, which
    reads like a malformed request rather than a missing prerequisite.
    """
    _, client = connect(args)
    if args.crawl:
        if not args.confirm:
            raise SquirrlyError(
                "crawling spends audit-page quota (this plan: 300 per blog per "
                "month). Pass --confirm."
            )
        client.allow_mutations = True
        registered = client.call("posts.audits", {"days_back": args.days})
        known = {row["permalink"]: row["user_post_id"]
                 for row in (registered.values() if isinstance(registered, dict) else [])}
        done = []
        for url in args.crawl:
            post_id = known.get(url)
            if post_id is None:
                made = client.call("posts.set_audit", {"permalink": url})
                post_id = made.get("user_post_id") if isinstance(made, dict) else None
                if post_id is None:
                    raise SquirrlyError(
                        f"posts.set_audit accepted {url} but returned no "
                        "user_post_id, so the row cannot be crawled or removed. "
                        "Check the account's audit-page quota before retrying."
                    )
                warn(f"registered {url} as audit page {post_id}")
            client.call("posts.crawl", {"url": url, "post_id": post_id})
            done.append({"url": url, "user_post_id": post_id})
        emit({"crawled": done,
              "next": "re-run `audit` without --crawl; the Cloud needs a moment"},
             args.output)
        return 0

    audit = client.call("audits.audit", {"days_back": args.days})
    audit = decode_embedded_json(audit) if isinstance(audit, str) else audit
    if not isinstance(audit, dict) or not audit:
        warn("no audit exists yet for this brand. Register and crawl a page "
             "first: audit --crawl <url> --confirm")
        emit({"score": UNKNOWN, "pages": 0, "incomplete": []}, args.output)
        return 0

    urls = audit.get("urls") or {}
    incomplete = []
    graded = 0
    for group, tasks in (audit.get("audit") or {}).items():
        for task in tasks:
            graded += 1
            if task.get("complete"):
                continue
            affected = task.get("urls")
            incomplete.append({
                "group": group,
                "task": task.get("audit_task"),
                "pages": [urls.get(str(x), x) for x in affected]
                         if isinstance(affected, list) and affected else [],
            })
    emit({
        "score": audit.get("score", UNKNOWN),
        "audit_id": audit.get("id", UNKNOWN),
        "audited_at": audit.get("audit_datetime", UNKNOWN),
        "in_progress": audit.get("in_progress"),
        "pages": len(urls),
        "tasks_graded": graded,
        "incomplete": incomplete,
    }, args.output)
    return 0


def cmd_add_brand(args: argparse.Namespace) -> int:
    """Register a new URL as a blog under this account.

    Ordering is the whole design. The site key is generated here and the Cloud
    never gives it back, so it is written to 1Password BEFORE the connect call.
    A failed connect leaves an unused item -- one delete. A successful connect
    whose key was never stored strands the blog permanently, because every later
    request for it has to carry a signature made with that key.
    """
    registry = Registry.load(args.config)
    if any(s.site_id == args.brand for s in registry.sites):
        raise SquirrlyError(
            f"{args.brand!r} is already in the registry. Adding it again would "
            "mint a second site key for a blog that already has one."
        )
    donor = registry.select(args.borrow_credential_from)
    if not args.confirm:
        raise SquirrlyError(
            "add-brand consumes one of the account's site slots and writes to "
            "1Password. Pass --confirm."
        )

    site_key = secrets.token_hex(32)
    site_uuid = str(uuid.uuid4())
    warn(f"generated a site key for {args.url}; storing it before connecting.")
    item_id = store_site_key(args.brand, args.url, site_key, site_uuid,
                             vault=args.vault)

    token = resolve_credential(donor.credential_ref)
    client = SquirrlyClient(token, args.url, allow_mutations=True)
    data = client.call("user.connect", {"site_key": site_key, "site_uuid": site_uuid})
    blog_id = (data or {}).get("user_blog_id") if isinstance(data, dict) else None
    if not blog_id:
        raise SquirrlyError(
            f"api/user/connect did not return a user_blog_id. The site key is "
            f"already stored as 1Password item {item_id} in {args.vault!r}; "
            "delete it before retrying so a stale key is not left behind."
        )

    emit({
        "brand": args.brand,
        "site_url": args.url,
        "blog_id": blog_id,
        "site_key_item": item_id,
        "next_step": (
            "add this brand to the registry with "
            f'credential_ref "{donor.credential_ref}", '
            f'site_key_ref "op://{args.vault}/{item_id}/credential", '
            f"blog_id {blog_id}"
        ),
    }, args.output)
    return 0


def store_site_key(brand: str, url: str, site_key: str, site_uuid: str,
                   *, vault: str) -> str:
    """Write the generated key to 1Password and return the new item id.

    Routed through the Service Account bridge, never bare `op`: this has to work
    from a scheduled run, where no one is present to answer a biometric prompt.
    """
    sys.path.insert(0, str(ONEPASSWORD_SCRIPTS))
    import bridge_router  # noqa: PLC0415
    from api_credential_template import run_api_credential_mutation  # noqa: PLC0415

    cmd = ["op", "item", "create", "--vault", vault, "--format", "json"]
    route = bridge_router.route_for_command(cmd, service_bridge_available=True)
    if route != "service_account":
        raise SquirrlyError(
            f"refusing to store the site key over the {route!r} route; start the "
            "Service Account bridge first."
        )
    notes = (
        f"HMAC signing key for the Squirrly Cloud API (X-SQ-Sig), site {url}.\n"
        f"site_uuid: {site_uuid}\n"
        "Source: generated by squirrly-ops add-brand. The Cloud never returns "
        "this value, so this item is the ONLY copy.\n"
        "IMPORTANT: the HMAC key is the RAW 32 BYTES, i.e. bytes.fromhex(this "
        "value). Signing with the hex string is rejected with the same "
        "'signature_required' the server sends for no signature at all."
    )
    template = {
        "title": f"Squirrly Site Key (HMAC) - {brand}",
        "category": "API_CREDENTIAL",
        "fields": [
            {"id": "credential", "type": "CONCEALED", "label": "credential", "value": ""},
            {"id": "notesPlain", "type": "STRING", "label": "notesPlain", "value": ""},
            {"id": "hostname", "type": "STRING", "label": "hostname", "value": ""},
        ],
    }
    result = run_api_credential_mutation(
        cmd, template,
        {"credential": site_key, "notesPlain": notes, "hostname": "api.squirrly.co"},
        runner=bridge_router.run_command, timeout=180,
    )
    # discard_output=True keeps the created item's JSON (which contains the
    # key we just wrote) out of this process's stdout, so the id is read back
    # by title instead of parsed out of a secret-bearing payload.
    del result
    listing = bridge_router.run_command(
        ["op", "item", "list", "--vault", vault, "--format", "json"], timeout=120)
    for item in json.loads(listing.get("stdout") or "[]"):
        if item.get("title") == template["title"]:
            return item["id"]
    raise SquirrlyError(
        f"stored the key but could not find item {template['title']!r} in {vault!r}."
    )


def cmd_raw(args: argparse.Namespace) -> int:
    _, client = connect(args)
    params: dict[str, Any] = {}
    for pair in args.param or []:
        if "=" not in pair:
            raise SquirrlyError(f"--param expects key=value, got {pair!r}")
        key, value = pair.split("=", 1)
        params[key] = value
    emit(client.call(args.op, params), args.output)
    return 0


# --------------------------------------------------------------------------
# argument parsing
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    # Global flags are declared on a parent parser and attached to every
    # subcommand as well, so `--site x plan` and `plan --site x` both work.
    # argparse otherwise accepts them only before the subcommand, which is the
    # position nobody reaches for.
    # default=SUPPRESS is load-bearing. Because the same flags are attached to
    # the main parser AND every subparser, an ordinary default would be applied
    # twice: the subparser would write its own `None` over the value the user
    # gave before the subcommand, so `--site x plan` would silently lose the
    # brand. With SUPPRESS an unsupplied flag sets nothing, and the real
    # defaults come from set_defaults() below.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--site", default=argparse.SUPPRESS,
                        help="brand id from the registry (required by account commands)")
    common.add_argument("--config", default=argparse.SUPPRESS,
                        help="registry path (default ~/.config/squirrly-ops/sites.json)")
    common.add_argument("--output", choices=["table", "json"], default=argparse.SUPPRESS)
    common.add_argument("--confirm", action="store_true", default=argparse.SUPPRESS,
                        help="allow an operation that changes state or spends quota")

    parser = argparse.ArgumentParser(
        prog="squirrly-ops",
        description="Multi-brand CLI for the Squirrly SEO cloud API.",
        parents=[common],
    )
    # NOT set_defaults(): it reaches into the shared action objects and rewrites
    # action.default, which would undo the SUPPRESS above for every subparser at
    # once (parents= shares action instances, it does not clone them). Defaults
    # are applied after parsing instead, by parse_args().
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name: str, help_text: str) -> argparse.ArgumentParser:
        return sub.add_parser(name, help=help_text, parents=[common])

    add("sites", "list configured brands").set_defaults(func=cmd_sites)

    ops = add("ops", "list every known API operation, its verb, and what gates it")
    ops.add_argument("--gate", choices=sorted(GATE_REASONS),
                     help="only operations blocked by this gate")
    ops.set_defaults(func=cmd_ops)

    add_brand = add("add-brand", "register a new site URL as a blog on this account")
    add_brand.add_argument("--brand", required=True, help="registry id to use for the new brand")
    add_brand.add_argument("--url", required=True, help="the exact site URL, e.g. https://example.com")
    add_brand.add_argument("--borrow-credential-from", required=True,
                           help="an existing brand whose account USER-TOKEN to reuse "
                                "(the token is account-scoped; USER-URL picks the blog)")
    add_brand.add_argument("--vault", default=os.environ.get("SQUIRRLY_OPS_OP_VAULT", "Automation"),
                           help="1Password vault for the generated site key")
    add_brand.set_defaults(func=cmd_add_brand)
    add("doctor", "prove the credential and connection work").set_defaults(func=cmd_doctor)
    add("plan", "subscription, site slots, and remaining quota").set_defaults(func=cmd_plan)

    checks = add("checks", "SEO health checks for this site")
    checks.add_argument("--todo", action="store_true", help="only checks that are not done")
    checks.set_defaults(func=cmd_checks)

    audit = add("audit", "the site audit score and every incomplete task")
    audit.add_argument("--days", type=int, default=30,
                       help="days_back window; omitted the server returns an empty list")
    audit.add_argument("--crawl", action="append", metavar="URL",
                       help="register and crawl this URL first (repeatable, spends quota)")
    audit.set_defaults(func=cmd_audit)

    add("keywords", "the keyword briefcase").set_defaults(func=cmd_keywords)

    research = add("research", "keyword research results")
    research.add_argument("--keyword", help="substring filter")
    research.add_argument("--all", action="store_true",
                          help="page through every result instead of the first page")
    research.set_defaults(func=cmd_research)

    focus = add("focus", "focus pages and their audits")
    focus.add_argument("--full", action="store_true", help="include the full decoded audit payload")
    focus.set_defaults(func=cmd_focus)

    add("ai-visibility", "share of traffic arriving from AI sources").set_defaults(
        func=cmd_ai_visibility)

    dash = add("dashboard", "mint a one-shot cloud dashboard login link")
    dash.add_argument("--print-url", action="store_true",
                      help="print the link instead of opening it (it is a live credential)")
    dash.set_defaults(func=cmd_dashboard)

    inspire = add("inspire", "research a topic across blog / wiki / twitter / images")
    inspire.add_argument("query", help="the topic to research")
    inspire.add_argument("--source", choices=sorted(INSPIRE_SOURCES),
                         help="one source only (default: all four)")
    inspire.set_defaults(func=cmd_inspire)

    raw = add("raw", "call any known operation directly")
    raw.add_argument("op", help="operation name from `ops`")
    raw.add_argument("--param", action="append", help="key=value, repeatable")
    raw.set_defaults(func=cmd_raw)

    return parser


GLOBAL_DEFAULTS = {"site": None, "config": None, "output": "table", "confirm": False}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse, then fill in the defaults the SUPPRESS'd global flags omit."""
    args = build_parser().parse_args(argv)
    for name, default in GLOBAL_DEFAULTS.items():
        if not hasattr(args, name):
            setattr(args, name, default)
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        return args.func(args)
    except SquirrlyError as exc:
        print(f"[squirrly-ops] error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
