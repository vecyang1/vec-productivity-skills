"""Guard the one inference forum_sweep exists to make.

A forum channel answers `dc history` with `fetched: 0` and no error, so the
dangerous outcome is not a crash -- it is a confident, wrong "that channel is
quiet". These tests are written against that failure: every assertion below is
about telling *unreachable* apart from *empty*.

Hermetic by construction. `sweep()` takes its CLI caller as an argument, so
nothing here needs DISCORD_TOKEN, a network, or a local store. A test that
needed the real token would only pass on a machine that already worked.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from forum_sweep import (  # noqa: E402
    FORUM_CHANNEL_TYPE,
    classify_channels,
    partition_hits,
    sweep,
)

# One forum, one ordinary channel. Thread ids are deliberately absent from it --
# that absence is the whole detection mechanism.
CHANNELS = [
    {"id": "100", "name": "releases-and-updates", "type": 0},
    {"id": "200", "name": "community-help", "type": FORUM_CHANNEL_TYPE},
]
THREAD_A = "9001"
THREAD_B = "9002"


def _fake_cli(search_hits, *, channels=None, channels_error=False):
    """Stand in for the discord CLI, returning already-unwrapped `data`."""
    calls = []

    def call(*args):
        calls.append(args)
        if args[:2] == ("dc", "channels"):
            if channels_error:
                return {"error": "exit_1"}
            return {"data": CHANNELS if channels is None else channels}
        if args[:2] == ("dc", "search"):
            return {"data": list(search_hits.get(args[3], []))}
        if args[:2] == ("dc", "history"):
            # A real forum id would answer 0 here; a thread id answers with rows.
            if args[2] == "200":
                return {"data": {"fetched": 0, "stored": 0}}
            return {"data": {"fetched": 3, "stored": 3}}
        raise AssertionError("unexpected command: %r" % (args,))

    call.calls = calls
    return call


def test_forum_channels_are_identified_and_still_counted_as_known() -> None:
    """A forum's own id is known; only its threads are not.

    Getting this backwards would classify every forum hit as a thread hit and
    the detector would report noise as a discovery.
    """
    result = classify_channels(CHANNELS)

    assert [f["name"] for f in result["forums"]] == ["community-help"]
    assert set(result["known"]) == {"100", "200"}, "forum id must stay in the known set"


def test_partition_separates_thread_hits_from_channel_hits_in_both_directions() -> None:
    known = classify_channels(CHANNELS)["known"]

    parts = partition_hits(
        [
            {"channel_id": "100", "content": "ordinary channel message"},
            {"channel_id": THREAD_A, "content": "forum post reply"},
        ],
        known,
    )

    # Both directions asserted: a known id must NOT be called a thread, and an
    # unknown id must be. One-directional coverage here passes while the
    # detector is stuck saying "everything is a thread".
    assert len(parts["in_channel"]) == 1
    assert parts["in_channel"][0]["channel_id"] == "100"
    assert len(parts["in_thread"]) == 1
    assert parts["in_thread"][0]["channel_id"] == THREAD_A


def test_search_reaches_threads_that_history_reports_as_empty() -> None:
    """The regression this script exists for.

    The forum answers history with fetched: 0. If the sweep trusted that, it
    would report nothing. It must still surface the threads that search found.
    """
    call = _fake_cli({"selector": [
        {"channel_id": THREAD_A, "timestamp": "2026-07-25T00:00:00", "content": "1.1.75 shipped"},
        {"channel_id": THREAD_B, "timestamp": "2026-08-09T00:00:00", "content": "new block"},
        {"channel_id": "100", "timestamp": "2026-06-04T00:00:00", "content": "announcement"},
    ]})

    report = sweep(call, "guild-1", ["selector"], limit=25)

    assert report["threads_discovered"] == 2, "thread hits were lost"
    assert report["queries"]["selector"]["hits"] == 3
    assert report["queries"]["selector"]["in_thread"] == 2
    # Newest first, so a caller reading the head gets current activity.
    assert report["threads"][0]["thread_id"] == THREAD_B


def test_report_never_claims_a_forum_is_inactive() -> None:
    """Prose in a receipt becomes a conclusion someone repeats."""
    call = _fake_cli({"selector": []})

    report = sweep(call, "guild-1", ["selector"], limit=25)

    assert report["threads_discovered"] == 0
    note = report["note"].lower()
    assert "not inactive" in note, "an unreached forum must not read as a quiet one"
    # The forum must still be listed, so a zero result is visibly incomplete
    # rather than looking like a fully-covered empty server.
    assert [f["name"] for f in report["forum_channels"]] == ["community-help"]


def test_message_bodies_are_withheld_unless_requested() -> None:
    hits = {"selector": [
        {"channel_id": THREAD_A, "timestamp": "t", "content": "private text", "sender_name": "someone"}
    ]}

    redacted = sweep(_fake_cli(hits), "g", ["selector"])
    sample = redacted["queries"]["selector"]["samples"][0]
    assert "content" not in sample and "sender" not in sample
    assert "private text" not in json.dumps(redacted)

    opted_in = sweep(_fake_cli(hits), "g", ["selector"], include_text=True)
    assert opted_in["queries"]["selector"]["samples"][0]["content"] == "private text"


def test_threads_can_be_read_in_full_because_a_thread_is_a_channel() -> None:
    call = _fake_cli({"q": [{"channel_id": THREAD_A, "timestamp": "t"}]})

    report = sweep(call, "g", ["q"], read_threads=1)

    assert report["thread_reads"][0]["result"] == {"fetched": 3, "stored": 3}
    assert ("dc", "history", THREAD_A, "-n", "25", "--channel-name", "thread-%s" % THREAD_A) in call.calls


def test_a_failed_channel_list_is_an_error_not_an_empty_sweep() -> None:
    """Without this, an auth failure renders as a server with no forums."""
    report = sweep(_fake_cli({}, channels_error=True), "g", ["q"])

    assert "error" in report
    assert "threads_discovered" not in report


def test_sweep_needs_no_token_or_network() -> None:
    """Proves the hermetic claim rather than assuming it."""
    saved = os.environ.pop("DISCORD_TOKEN", None)
    try:
        report = sweep(_fake_cli({"q": []}), "g", ["q"])
        assert report["channel_count"] == 2
    finally:
        if saved is not None:
            os.environ["DISCORD_TOKEN"] = saved


if __name__ == "__main__":
    ns = dict(globals())
    failures = 0
    for name, fn in sorted(ns.items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS %s" % name)
            # Catch Exception, not just AssertionError: broken logic usually
            # surfaces as IndexError/KeyError first, and letting that escape
            # aborts the run so every later test silently never executes --
            # which reads as a shorter passing suite.
            except Exception as exc:  # noqa: BLE001
                failures += 1
                print("FAIL %s: %s: %s" % (name, type(exc).__name__, exc))
    print("%d failed" % failures)
    raise SystemExit(1 if failures else 0)
