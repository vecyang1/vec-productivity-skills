#!/usr/bin/env python3
"""Reach Discord forum-channel content, which channel-level reads cannot see.

Why this is a script and not advice: `GET /guilds/{id}/channels` never returns
threads, so a forum channel (`type: 15`) answers `dc history` with
`fetched: 0` and no error. The busiest support channel on a server therefore
renders as empty, and that emptiness reads as "the community is quiet". It is
not -- the posts are threads, and Discord's own server-side search does index
them. Measured once: a release that had shipped six weeks earlier existed only
inside forum threads while the announcement channel showed nothing newer than
the previous version.

The route, both halves already in the CLI:

    dc search  GUILD "keyword"   -- server-side; DOES index thread content
    dc history THREAD_ID         -- a thread is a channel, so this reads it

A hit is identified as living in a thread when its channel_id is absent from
the `dc channels` set. That is the whole trick, and it is why this script needs
the channel list before it needs the search.

Requires DISCORD_TOKEN in the environment. Never pass a token on the command
line. The intended unattended caller is the 1Password Service Account
fixed-command adapter (SKILL.md, "Credential Lane"), which passes NO argv and
discards child stdout -- so with no arguments this reads ./forum_sweep.config.json
from the working directory and always writes its own receipt.

Redacted by default: channel names, thread ids, counts and timestamps only,
never message bodies or sender names. --include-text opts in, for when the
requester actually asked to read the posts.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable, Iterable, Sequence

FORUM_CHANNEL_TYPE = 15
CMD_TIMEOUT = int(os.environ.get("DISCORD_FORUM_TIMEOUT", "120"))
DEFAULT_SINK = os.environ.get(
    "DISCORD_FORUM_SINK", str(Path.home() / ".cache/discord-cli-forum/sweep.out")
)
DEFAULT_CONFIG = "forum_sweep.config.json"


def resolve_cli() -> str | None:
    """Prefer an explicit override, then PATH, then the uv tool location."""
    if explicit := os.environ.get("DISCORD_CLI"):
        return explicit if Path(explicit).exists() else None
    if found := shutil.which("discord"):
        return found
    uv = Path.home() / ".local/share/uv/tools/kabi-discord-cli/bin/discord"
    return str(uv) if uv.exists() else None


def make_caller(cli: str, timeout: int = CMD_TIMEOUT) -> Callable[..., dict]:
    """Build the real subprocess caller, unwrapping the CLI's result envelope.

    Every --json command answers {ok, schema_version, data}. Returning `data`
    directly is deliberate: reading the envelope as the payload is the failure
    that makes a healthy account look unauthenticated.
    """

    def call(*args: str) -> dict:
        proc = subprocess.run(
            [cli, *args, "--json"], capture_output=True, text=True, timeout=timeout
        )
        if proc.returncode != 0:
            # dc history raises for status on an unreadable channel. That is an
            # authorization boundary, not a bug to retry around.
            return {"error": "exit_%d" % proc.returncode}
        try:
            envelope = json.loads(proc.stdout)
        except json.JSONDecodeError:
            return {"error": "unparseable"}
        if not envelope.get("ok"):
            return {"error": "not_ok", "detail": envelope.get("error")}
        return {"data": envelope.get("data")}

    return call


def classify_channels(channels: Iterable[dict]) -> dict:
    """Split a guild's channel list into forums and the known-id set.

    The known-id set is the reference the thread test depends on, so it must
    include every channel -- forums included. A forum's own id is "known"; its
    threads' ids are not, which is exactly what makes them detectable.
    """
    known: dict[str, str] = {}
    forums: list[dict] = []
    for row in channels:
        cid = str(row.get("id") or "")
        if not cid:
            continue
        name = str(row.get("name") or "")
        known[cid] = name
        if row.get("type") == FORUM_CHANNEL_TYPE:
            forums.append({"id": cid, "name": name})
    return {"known": known, "forums": forums}


def partition_hits(hits: Iterable[dict], known: dict) -> dict:
    """Separate search hits that came from threads from ordinary channel hits."""
    in_channel: list[dict] = []
    in_thread: list[dict] = []
    for hit in hits:
        cid = str(hit.get("channel_id") or "")
        (in_channel if cid in known else in_thread).append(hit)
    return {"in_channel": in_channel, "in_thread": in_thread}


def _redact(hit: dict, include_text: bool) -> dict:
    row = {
        "channel_id": str(hit.get("channel_id") or ""),
        "timestamp": hit.get("timestamp"),
    }
    if include_text:
        row["sender"] = hit.get("sender_name")
        row["content"] = (hit.get("content") or "")[:1000]
    return row


def sweep(
    call: Callable[..., dict],
    guild: str,
    queries: Sequence[str],
    *,
    limit: int = 25,
    read_threads: int = 0,
    include_text: bool = False,
) -> dict:
    """Discover forum-thread content in one guild. `call` is injected for tests."""
    report: dict = {"guild": guild, "queries": {}}

    channels_res = call("dc", "channels", guild)
    if channels_res.get("error"):
        report["error"] = "channels_failed: %s" % channels_res["error"]
        return report
    classified = classify_channels(channels_res.get("data") or [])
    known = classified["known"]
    report["channel_count"] = len(known)
    report["forum_channels"] = classified["forums"]

    threads: dict[str, dict] = {}
    for query in queries:
        res = call("dc", "search", guild, query, "-n", str(limit))
        if res.get("error"):
            report["queries"][query] = {"error": res["error"]}
            continue
        hits = res.get("data") or []
        parts = partition_hits(hits, known)
        for hit in parts["in_thread"]:
            cid = str(hit.get("channel_id") or "")
            slot = threads.setdefault(cid, {"hits": 0, "newest": None})
            slot["hits"] += 1
            ts = hit.get("timestamp")
            if ts and (slot["newest"] is None or str(ts) > str(slot["newest"])):
                slot["newest"] = ts
        report["queries"][query] = {
            "hits": len(hits),
            "in_thread": len(parts["in_thread"]),
            "samples": [_redact(h, include_text) for h in parts["in_thread"][:5]],
        }

    report["threads_discovered"] = len(threads)
    report["threads"] = [
        {"thread_id": cid, **meta}
        for cid, meta in sorted(
            threads.items(), key=lambda kv: str(kv[1]["newest"] or ""), reverse=True
        )
    ]

    # A thread is a channel, so dc history reads it in full.
    if read_threads:
        reads = []
        for entry in report["threads"][:read_threads]:
            tid = entry["thread_id"]
            res = call("dc", "history", tid, "-n", str(limit), "--channel-name", "thread-%s" % tid)
            reads.append(
                {
                    "thread_id": tid,
                    "result": res.get("data") or {"error": res.get("error")},
                }
            )
        report["thread_reads"] = reads

    # The finding that motivates this script: a forum that no query reached is
    # NOT evidence of a quiet channel, and must never be reported as one.
    reached = {t["thread_id"] for t in report["threads"]}
    report["note"] = (
        "Forum channels hold no linear messages; %d thread(s) reached via search. "
        "Forums with no hits are unsearched by these keywords, NOT inactive."
        % len(reached)
    )
    return report


def load_config(path: Path) -> dict:
    """Read the no-argv configuration the fixed-command adapter relies on."""
    if not path.is_file():
        raise SystemExit(
            "no arguments and no %s in %s -- the unattended adapter passes no argv, "
            "so its configuration must live in a file under the spec's cwd" % (path.name, path.parent)
        )
    return json.loads(path.read_text(encoding="utf-8"))


def emit(report: dict, sink: Path) -> None:
    text = json.dumps(report, indent=2, ensure_ascii=False)
    sink.parent.mkdir(parents=True, exist_ok=True)
    sink.write_text(text, encoding="utf-8")
    sink.chmod(0o600)
    if sys.stdout.isatty():
        sys.stdout.write(text + "\n")
        sys.stdout.write("\nreceipt: %s\n" % sink)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--guild", help="Guild ID or name.")
    ap.add_argument("--query", action="append", default=[], help="Search term; repeatable.")
    ap.add_argument("-n", "--limit", type=int, default=25, help="Max hits per query.")
    ap.add_argument("--threads", type=int, default=0, help="Read the N newest threads in full.")
    ap.add_argument("--include-text", action="store_true", help="Include message bodies.")
    ap.add_argument("--sink", type=Path, default=Path(DEFAULT_SINK))
    ap.add_argument("--config", type=Path, help="Config file (default ./%s)." % DEFAULT_CONFIG)
    args = ap.parse_args()

    guild, queries = args.guild, list(args.query)
    limit, threads, include_text = args.limit, args.threads, args.include_text
    sink = args.sink

    if not guild or not queries:
        cfg = load_config(args.config or Path.cwd() / DEFAULT_CONFIG)
        guild = guild or cfg.get("guild")
        queries = queries or list(cfg.get("queries") or [])
        limit = cfg.get("limit", limit)
        threads = cfg.get("threads", threads)
        include_text = cfg.get("include_text", include_text)
        if cfg.get("sink"):
            sink = Path(cfg["sink"])

    if not guild or not queries:
        raise SystemExit("a guild and at least one query are required")

    cli = resolve_cli()
    if cli is None:
        raise SystemExit("discord CLI not found; see SKILL.md Preflight")
    if not os.environ.get("DISCORD_TOKEN"):
        raise SystemExit("DISCORD_TOKEN not set; see SKILL.md Credential Lane")

    # Isolate the local store so a sweep neither pollutes nor is flattered by
    # the real cache, and no purge is needed afterwards.
    with tempfile.TemporaryDirectory(prefix="discord-forum-") as tmp:
        os.environ["DB_PATH"] = str(Path(tmp) / "messages.db")
        os.environ["DATA_DIR"] = tmp
        report = sweep(
            make_caller(cli),
            guild,
            queries,
            limit=limit,
            read_threads=threads,
            include_text=include_text,
        )

    emit(report, sink)
    return 1 if report.get("error") else 0


if __name__ == "__main__":
    raise SystemExit(main())
