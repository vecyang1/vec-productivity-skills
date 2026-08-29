#!/usr/bin/env python3
"""Prove a discord-cli setup works end to end, against the real Discord API.

Why this is a script and not a checklist: the per-command payload shapes in
references/troubleshooting.md are a current fact about an upstream package, and
a current fact written in prose is a future lie. This exercises them live, so a
kabi-discord-cli release that changes the envelope fails here instead of
silently rotting the table.

Requires DISCORD_TOKEN in the environment. Never pass a token on the command
line. The intended caller is the 1Password Service Account fixed-command
adapter (see SKILL.md, "Credential Lane"), which discards child stdout -- use
--sink in that case.

Two properties that make the result trustworthy:

  * Isolated store. DB_PATH/DATA_DIR are redirected to a temp sqlite file, so
    the run can neither pollute nor be flattered by an existing local cache,
    and the destructive purge stage runs against a fixture only.
  * Redacted receipt. Stage outcomes, counts and shapes only -- never message
    bodies or sender names. Proving the flow works must not drag private chat
    content into an agent transcript or a log.

Exit 0 only when every stage passes.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DEFAULT_LIMIT = int(os.environ.get("DISCORD_E2E_LIMIT", "25"))
DEFAULT_MAX_CHANNELS = int(os.environ.get("DISCORD_E2E_MAX_CHANNELS", "8"))
DEFAULT_GUILDS = int(os.environ.get("DISCORD_E2E_MAX_GUILDS", "4"))
CMD_TIMEOUT = int(os.environ.get("DISCORD_E2E_TIMEOUT", "90"))
DEFAULT_SINK = os.environ.get(
    "DISCORD_E2E_SINK", str(Path.home() / ".cache/discord-cli-e2e/e2e.out"))


def resolve_cli() -> str | None:
    """Prefer an explicit override, then PATH, then the uv tool location."""
    if explicit := os.environ.get("DISCORD_CLI"):
        return explicit if Path(explicit).exists() else None
    if found := shutil.which("discord"):
        return found
    uv = Path.home() / ".local/share/uv/tools/kabi-discord-cli/bin/discord"
    return str(uv) if uv.exists() else None


class Run:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.failures: list[str] = []

    def log(self, line: str = "") -> None:
        self.lines.append(line)

    def stage(self, name: str, ok: bool, detail: str) -> bool:
        self.lines.append(f"[{'PASS' if ok else 'FAIL'}] {name} :: {detail}")
        if not ok:
            self.failures.append(name)
        return ok

    def emit(self, sink: Path) -> None:
        """Always leave a durable receipt; echo it only when someone can see it.

        The fixed-command adapter takes no arguments and discards child stdout,
        so a zero-arg run must still land its result somewhere findable.
        """
        text = "\n".join(self.lines) + "\n"
        sink.parent.mkdir(parents=True, exist_ok=True)
        sink.write_text(text)
        sink.chmod(0o600)
        if sys.stdout.isatty():
            sys.stdout.write(text)
            sys.stdout.write(f"\nreceipt: {sink}\n")


def unwrap(proc: subprocess.CompletedProcess):
    """Parse stdout and strip the {ok, schema_version, data} envelope.

    Every structured command routes through cli/_output.emit_structured, which
    wraps even bare lists. Reading the envelope as the payload makes a healthy
    account report authenticated=False -- see references/troubleshooting.md.
    """
    text = (proc.stdout or "").strip()
    payload = None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        for opener, closer in (("{", "}"), ("[", "]")):
            start, end = text.find(opener), text.rfind(closer)
            if start != -1 and end > start:
                try:
                    payload = json.loads(text[start : end + 1])
                    break
                except json.JSONDecodeError:
                    continue
    if isinstance(payload, dict) and "ok" in payload and "schema_version" in payload:
        return payload.get("data") if payload.get("ok") else None
    return payload


def pick_search_term(db_path: Path) -> tuple[str, str]:
    """Choose a term known to exist in the corpus: latin word, else CJK bigram."""
    if not db_path.exists():
        return "", ""
    con = sqlite3.connect(db_path)
    contents = [
        c for (c,) in con.execute(
            "SELECT content FROM messages WHERE content IS NOT NULL "
            "AND length(content) > 3 LIMIT 200"
        ) if c
    ]
    con.close()
    for content in contents:
        if tokens := re.findall(r"[A-Za-z]{4,12}", content):
            return tokens[0], "latin word"
    for content in contents:
        if cjk := re.findall(r"[一-鿿぀-ヿ]{2}", content):
            return cjk[0], "CJK bigram"
    return "", ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sink", type=Path, default=Path(DEFAULT_SINK),
                    help=f"where to write the receipt (default {DEFAULT_SINK}); "
                         "it is echoed to stdout only when stdout is a terminal")
    ap.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                    help=f"messages per channel (default {DEFAULT_LIMIT})")
    ap.add_argument("--max-channels", type=int, default=DEFAULT_MAX_CHANNELS,
                    help="stop after this many channels with traffic")
    ap.add_argument("--max-guilds", type=int, default=DEFAULT_GUILDS,
                    help="how many servers to probe for a readable channel")
    args = ap.parse_args()

    r = Run()
    cli = resolve_cli()
    if not cli:
        r.stage("0 cli", False, "discord binary not found; set DISCORD_CLI or "
                                "run: uv tool install kabi-discord-cli")
        r.emit(args.sink)
        return 127
    if not os.environ.get("DISCORD_TOKEN"):
        r.stage("0 credential", False,
                "DISCORD_TOKEN absent -- inject it, do not pass it as an argument")
        r.emit(args.sink)
        return 78

    workdir = Path(tempfile.mkdtemp(prefix="discord-e2e-"))
    db_path = workdir / "e2e.db"
    env = {**os.environ, "DB_PATH": str(db_path), "DATA_DIR": str(workdir),
           "NO_COLOR": "1", "TERM": "dumb"}

    def run(*a: str):
        started = time.monotonic()
        proc = subprocess.run([cli, *a], env=env, capture_output=True,
                              text=True, timeout=CMD_TIMEOUT)
        return proc, round(time.monotonic() - started, 1)

    r.log(f"cli            : {cli}")
    r.log(f"isolated store : {db_path}")
    r.log(f"limits         : {args.limit} msgs/channel, "
          f"{args.max_channels} channels, {args.max_guilds} servers")
    r.log("")

    try:
        proc, secs = run("status", "--json")
        data = unwrap(proc) or {}
        authed = isinstance(data, dict) and bool(data.get("authenticated"))
        r.stage("1 status", authed, f"authenticated={authed} {secs}s")
        if not authed:
            r.log(f"      parsed : {str(data)[:200]}")
            r.log(f"      stderr : {(proc.stderr or '').strip()[:300]}")
            return 1

        proc, secs = run("whoami", "--json")
        me = (unwrap(proc) or {}).get("user") or {}   # whoami nests under "user"
        r.stage("2 whoami", bool(me.get("id")),
                f"user_id={me.get('id')} mfa={me.get('mfa_enabled')} {secs}s")

        proc, secs = run("dc", "guilds", "--json")
        guilds = unwrap(proc) or []
        owned = [g for g in guilds if g.get("owner")]
        if not r.stage("3 dc guilds", isinstance(guilds, list) and bool(guilds),
                       f"{len(guilds)} servers ({len(owned)} owned) {secs}s"):
            return 1

        # Owned servers first: the cleanest authorization boundary to read.
        candidates = owned + [g for g in guilds if not g.get("owner")]

        # Probe a spread rather than stopping at the first channel with any
        # traffic. A one-message corpus makes every downstream stage pass while
        # proving nothing -- no search, no aggregation, no paging.
        probed: list[tuple[dict, dict, int, int]] = []
        unreadable = 0
        for guild in candidates[: args.max_guilds]:
            if len(probed) >= args.max_channels:
                break
            proc, _ = run("dc", "channels", str(guild["id"]), "--json")
            channels = unwrap(proc) or []
            if not isinstance(channels, list) or not channels:
                r.log(f"      probe: {guild['name']}: 0 readable text channels")
                continue
            r.log(f"      probe: {guild['name']}: {len(channels)} text channels")
            for ch in channels[:4]:
                if len(probed) >= args.max_channels:
                    break
                proc, _ = run("dc", "history", str(ch["id"]), "-n", str(args.limit),
                              "--guild-name", str(guild["name"]),
                              "--channel-name", str(ch["name"]), "--json")
                if proc.returncode != 0:
                    unreadable += 1        # authorization boundary, not a bug
                    continue
                # history emits {"fetched": N, "stored": M}, not a message list.
                res = unwrap(proc)
                fetched = res.get("fetched", 0) if isinstance(res, dict) else 0
                stored = res.get("stored", 0) if isinstance(res, dict) else 0
                r.log(f"      probe:   #{ch['name']}: fetched={fetched} stored={stored}")
                if fetched > 0:
                    probed.append((guild, ch, fetched, stored))
        if unreadable:
            r.log(f"      probe: {unreadable} channel(s) not readable by this "
                  f"account (expected)")

        if not probed:
            r.stage("4 dc channels + 5 dc history", False,
                    "no readable channel with messages found")
            return 1

        probed.sort(key=lambda p: p[2], reverse=True)
        guild, ch, fetched, stored = probed[0]
        total = sum(p[2] for p in probed)
        r.stage("4 dc channels", True,
                f"{len(probed)} channels with traffic; driving flow from "
                f"'{guild['name']}' -> #{ch['name']}")
        # >1 on the busiest channel: a single message cannot exercise search or
        # aggregation, so treat that as an inconclusive run, not a pass.
        r.stage("5 dc history", fetched > 1,
                f"{total} messages across {len(probed)} channels; "
                f"busiest #{ch['name']} = {fetched} (stored {stored})")

        con = sqlite3.connect(db_path)
        rows = con.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        senders = con.execute(
            "SELECT COUNT(DISTINCT sender_id) FROM messages").fetchone()[0]
        con.close()
        r.stage("6 local store", rows > 0,
                f"{rows} rows persisted, {senders} distinct senders")

        proc, secs = run("dc", "sync", str(ch["id"]), "-n", "50", "--json")
        s = unwrap(proc)
        s = s if isinstance(s, dict) else {}
        r.stage("7 dc sync", proc.returncode == 0,
                f"fetched={s.get('fetched')} stored={s.get('stored')} "
                f"(0 stored is correct -- nothing new since history) {secs}s")

        term, kind = pick_search_term(db_path)
        if term:
            proc, _ = run("search", term, "-n", "20", "--json")
            hits = unwrap(proc)
            n = len(hits) if isinstance(hits, list) else 0
            r.stage("8 search", proc.returncode == 0 and n > 0,
                    f"{n} hits for an auto-selected {len(term)}-char {kind} "
                    f"known to exist in the corpus")
        else:
            r.stage("8 search", False, "no searchable term derivable from corpus")

        proc, _ = run("stats", "--json")
        st = unwrap(proc)
        st = st if isinstance(st, dict) else {}
        r.stage("9a stats", st.get("total", 0) > 0,
                f"total={st.get('total')} across "
                f"{len(st.get('channels') or [])} channel(s)")

        # These return plain lists; today may legitimately be empty.
        for name, argv, need_rows in (
            ("9b recent", ("recent", "-n", "5", "--json"), True),
            ("9c top", ("top", "-n", "5", "--json"), True),
            ("9d timeline", ("timeline", "--by", "day", "--json"), True),
            ("9e today", ("today", "--json"), False),
        ):
            proc, _ = run(*argv)
            payload = unwrap(proc)
            n = len(payload) if isinstance(payload, list) else -1
            r.stage(name, proc.returncode == 0 and (n > 0 if need_rows else n >= 0),
                    f"{n} rows")

        out = workdir / "export.json"
        proc, _ = run("export", str(ch["id"]), "-f", "json", "-o", str(out))
        size = out.stat().st_size if out.exists() else 0
        r.stage("10 export", proc.returncode == 0 and size > 0,
                f"wrote {size} bytes to a temp path (deleted after run)")

        def channel_rows() -> int:
            con = sqlite3.connect(db_path)
            n = con.execute("SELECT COUNT(*) FROM messages WHERE channel_id = ?",
                            (str(ch["id"]),)).fetchone()[0]
            con.close()
            return n

        before = channel_rows()
        proc, _ = run("purge", str(ch["id"]), "-y")
        after = channel_rows()
        con = sqlite3.connect(db_path)
        survivors = con.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        con.close()
        # Purge must clear the named channel and leave every other one alone.
        r.stage("11 purge", proc.returncode == 0 and before > 0 and after == 0,
                f"#{ch['name']} rows {before} -> {after}; {survivors} rows in "
                f"other channels untouched (fixture store only)")

        return 1 if r.failures else 0

    finally:
        shutil.rmtree(workdir, ignore_errors=True)
        r.log("")
        r.log(f"FAILURES: {r.failures if r.failures else 'none'}")
        r.emit(args.sink)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - the receipt must always be written
        sys.stderr.write(f"discord e2e harness crashed: "
                         f"{type(exc).__name__}: {str(exc)[:300]}\n")
        sys.exit(70)
