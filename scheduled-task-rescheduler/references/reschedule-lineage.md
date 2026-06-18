# Reschedule & Rebuild Lineage

A schedule change is not permission to lose history. Rescheduled, renamed, rebuilt, split, or merged recurring tasks must preserve their prior track.

## Capture Before You Change

Before touching the runtime, write down:

- the previous cadence ID and visible runtime name;
- the previous runtime ID (sidecar slug, LaunchAgent label, n8n workflow ID, cron entry);
- the previous **checkpoint path** and **success-marker pattern**;
- the **output owner(s)** the task already maintains;
- the **reason** for the reschedule / rebuild / split / merge.

## Decision Table

| Situation | Cadence ID | Checkpoint | What the new card must do |
|---|---|---|---|
| Same job, new time | **keep** | **keep** | bump `Updated`, note the time change in `Source Refs` |
| Same job, new name | **keep** | **keep** | keep the ID; the human name can change |
| New runtime (e.g. cron → Antigravity) | **keep** | **keep** | record old + new runtime IDs in `Source Refs` |
| Genuine fork / rebuild | **new** | migrate | reference the old ID + runtime path in `Source Refs`; read or migrate the old checkpoint before processing |
| Split one task into two | **new ×N** | partition | each successor states which slice of the old track it inherits and which state to ignore |
| Merge two tasks into one | **new** (or keep one) | merge | state which predecessors fold in; retire the others |

## The Hard Rule

**Do not write a new success marker until the successor has reused, migrated, or explicitly superseded the previous checkpoint.**

If the previous state is missing or ambiguous, write a review note under `.run/cadence/<new_id>/` and treat the first run as a **controlled catch-up**, not a blind rebuild. A blind rebuild silently re-emails, re-posts, or re-processes everything the old task already handled.

Keep retired predecessor cards in the registry long enough for a future agent to trace why the schedule changed. Mark them `Status: retired` and leave their `Source Refs` intact.

## Worked Examples

### Move a nightly job 02:30 → 01:00 (same job)

- Keep `CAD-20260101-example-digest`. Keep the checkpoint path.
- Update `Schedule Expression`, bump `Updated`.
- Append to `Source Refs`: `rescheduled 02:30->01:00 on 2026-03-04, reason: earlier credit window`.
- No checkpoint migration needed; the next run resumes from the same state.

### Split "morning sync" into "inbox sync" + "calendar sync"

- Retire `CAD-…-morning-sync` (`Status: retired`), leave its card in place.
- Create `CAD-…-inbox-sync` and `CAD-…-calendar-sync`.
- Each successor `Source Refs`: `split from CAD-…-morning-sync; inherits <inbox|calendar> cursor; ignores the other`.
- Partition the old checkpoint: copy the inbox cursor into the inbox card's state, the calendar cursor into the calendar card's state. Only then let either write a success marker.

### Swap runtime cron → Antigravity (same job)

- Keep the cadence ID and checkpoint path.
- `Source Refs`: `was cron '30 2 * * *' (crontab); now antigravity sidecar <slug>`.
- Disable the old cron entry **after** the Antigravity task is verified active (see `antigravity-activation.md`), so there is no gap and no double-run.

## Why This Matters

The checkpoint is what makes a recurring task incremental. Lose it during a reschedule and the task either starts from zero (expensive, and may duplicate side effects) or silently skips the gap between the old success marker and the new one. Lineage in `Source Refs` is what lets the next person — or the next agent — understand a schedule they did not create.
