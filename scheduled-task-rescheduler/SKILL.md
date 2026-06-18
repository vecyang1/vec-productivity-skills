---
name: scheduled-task-rescheduler
description: Safely reschedule, rename, rebuild, split, or merge recurring agent tasks (Antigravity, Codex, Claude Code, LaunchAgent, cron, n8n) without losing lineage or state. Use this skill when changing a recurring task's time/name/runtime/scope, when a scheduled task missed its window and you must decide whether to catch up, or when activating an Antigravity scheduled task via direct config editing. Preserves checkpoints, success markers, runtime IDs, output owners, and catch-up policy.
license: Complete terms in LICENSE.txt
---

# Scheduled Task Rescheduler

Reschedule recurring agent tasks **without amnesia**. A schedule change is not permission to lose history.

This skill is for anyone running recurring AI-agent jobs across one or more schedulers and wanting a single, durable contract per task instead of opaque settings scattered across runtime UIs.

## Core Model: The Runtime Is Just An Alarm Clock

A scheduler trigger — a cron line, an Antigravity sidecar, a LaunchAgent plist, an n8n cron node — is only an alarm clock. It tells you *when*, nothing more.

The **cadence card** (a durable Markdown record you own, in your repo or vault) is the source of truth for:

- **why** the task exists,
- **where** it runs (an exact absolute execution root, not a UI label),
- **what** prompt it runs,
- **how** it catches up after a miss,
- **when** it should stop or no-op.

If you edit the runtime but not the record, the next agent inherits a black box. Keep the record as the contract; treat the runtime as a switch that points at it.

→ Full field list and a copy-paste record: [`references/cadence-card-template.md`](references/cadence-card-template.md)

## The One Rule When Rescheduling

Before you change a recurring task's time, name, runtime, or scope, capture its **lineage** first:

1. previous cadence ID and visible runtime name,
2. previous runtime ID (sidecar slug, LaunchAgent label, n8n workflow ID),
3. previous **checkpoint path** and **success-marker pattern**,
4. the **output owner(s)** the task already maintains,
5. the **reason** for the change.

Then:

- **Same job, new time/name?** Keep the same cadence ID and checkpoint path.
- **Need a new ID/slug?** The new record must reference the old ID + runtime path in its `Source Refs`, and its prompt must **read or migrate the old checkpoint before processing new work**.
- **Split or merge?** Each successor states which part of the old track it inherits and which state to ignore. Keep the retired predecessor record long enough to trace why the schedule changed.
- **Never** write a new success marker until the successor has reused, migrated, or explicitly superseded the old checkpoint. If prior state is missing or ambiguous, drop a review note and treat the first run as a controlled catch-up, not a blind rebuild.

→ Worked examples (rename, new-ID, split, merge, runtime swap): [`references/reschedule-lineage.md`](references/reschedule-lineage.md)

## Incremental By Default

A recurring task should not start from zero every run. The reliable loop:

1. `cd` to the exact execution root.
2. Read the task's instructions and its cadence card.
3. Read the prior checkpoint + success marker.
4. Detect inputs changed since `last_success_at` / `last_cursor` / `input_signature`.
5. **No-op with a receipt** if nothing changed.
6. Resume from checkpoint if the last run died halfway.
7. Skip / pause / ask for review if catch-up policy says it's stale, risky, duplicated, or out of the credit window.
8. Update the output owner **first**.
9. Write the success marker **only after** the owner is safely updated.

Keep checkpoints as disposable runtime state under an ignored `.run/cadence/<id>/`, never as user-facing truth, and never commit them.

## Missed Runs & Credit

Choose a catch-up policy on purpose:

- `cheap_window_only` — expensive, non-urgent work. A missed 2 AM job does **not** fire after you wake, so it can't burn daytime credit.
- `catch_up_when_awake` — only when late execution is still valuable (sync, health, ops).
- `skip_if_stale` / `manual_review` — when a late run could double-write or mislead.

→ Catch-up, retry, and credit-window patterns: [`references/catch-up-and-credit.md`](references/catch-up-and-credit.md)

## Antigravity: Two-Layer Activation

An Antigravity scheduled task is **not** active just because a sidecar file exists. Three files must agree:

| File | Owns |
|---|---|
| `~/.gemini/config/sidecars/<slug>/sidecar.json` | schedule, display name, command, saved prompt |
| `~/.gemini/config/config.json` → `sidecars.<slug>` | `enabled: true` and `projectId` |
| `~/.gemini/config/projects/<projectId>.json` | UI project label + real folder URI |

The UI project label is **only a label**. The prompt must contain an explicit `cd "/absolute/execution/root"` because the project dropdown can be broader than the folder the task should run in.

Two activation paths:

- **Manual paste** — a human or agent creates the task in the UI. Mark the record `awaiting_manual_paste` until paste is confirmed; the payload must include Name, Project label, Schedule, and Prompt.
- **Direct config** — write all three files above, then verify enabled + project-bound + label-matched + prompt-rooted.

→ Step-by-step activation, verification, pause/retire, and JSON shapes: [`references/antigravity-activation.md`](references/antigravity-activation.md)

## Validate

After writing or editing a cadence record:

```bash
python3 scripts/validate_cadence_card.py path/to/your-cadence-records.md --strict
```

It checks required fields, status vocabulary, incremental-state completeness, and alias↔execution-root agreement. Wire it into your pre-commit or pre-claim gate. Pure standard-library Python 3 — no dependencies.

## Quick Checklist

- [ ] Cadence record exists and is the source of truth (runtime points at it)
- [ ] Execution root is an absolute path, not a UI label
- [ ] Lineage captured before any reschedule (old ID, runtime ID, checkpoint, output owner, reason)
- [ ] Old checkpoint reused / migrated / superseded before new success marker
- [ ] Catch-up + credit policy chosen deliberately
- [ ] (Antigravity) all three config files agree; prompt has an explicit `cd`
- [ ] Checkpoints under ignored `.run/cadence/<id>/`, never committed
- [ ] `validate_cadence_card.py` passes
