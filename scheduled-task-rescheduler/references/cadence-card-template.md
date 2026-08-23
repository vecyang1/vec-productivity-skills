# Cadence Card Template

A **cadence card** is one durable Markdown record per recurring task. Keep all cards in a single file (e.g. `cadence-records.md`) in your repo or vault. The runtime scheduler points at the card; the card never points at the runtime as its source of truth.

Card heading shape:

```markdown
### `CAD-YYYYMMDD-slug` - Human Name
```

The ID is stable for the life of the job. Keep it the same across reschedules; mint a new one only when you genuinely fork the track (see `reschedule-lineage.md`).

## Required Fields

| Field | Meaning |
|---|---|
| `Status` | Registry-level truth about whether the cadence should guide agents |
| `Activation Status` | Runtime activation state |
| `Activation Mode` | Whether an agent can self-schedule or a human must paste |
| `Created`, `Updated` | Dates in `YYYY-MM-DD` |
| `Created By`, `Planned By` | Actor trace |
| `Project Ref` | Project/task identity |
| `Execution Root`, `Root Alias` | Exact folder where the command runs (absolute path or alias) |
| `Runtime Project Label` | Runtime UI label when different from the root |
| `Primary Runtime`, `Runtime Systems` | Execution surfaces (antigravity, cron, launchd, n8n, ...) |
| `Schedule Frequency`, `Schedule Expression`, `Timezone` | Cadence definition |
| `Preferred Window`, `Credit Policy` | Timing / cost preference |
| `Catch Up Policy`, `Retry Policy`, `Retry Interval Minutes`, `Max Catch Up Age Hours` | Missed-run behavior |
| `Execution Mode`, `State Owner` | Incremental model |
| `Output Owner` | File or system updated by successful runs |
| `Side Effect Level`, `Requires Human Review`, `Network Required` | Safety |
| `Manual Paste Required`, `Manual Paste Payload` | Manual activation payload (Antigravity etc.) |
| `Source Refs` | Predecessor IDs, runtime paths, request/ticket pointers |

Incremental cards (`Execution Mode: incremental`) must also include:

| Field | Meaning |
|---|---|
| `Checkpoint Path` | Cursor/state file, normally under `.run/cadence/<id>/state.json` in the execution root |
| `Success Marker Pattern` | Period marker written only after a complete success |
| `Resume Policy` | How to resume after partial failure |
| `Stop Condition` | When to no-op, pause, or require review |

## Status Vocabulary

| Field | Allowed values |
|---|---|
| `Status` | `proposed`, `planned`, `active`, `paused`, `retired`, `needs_prompt_recovery` |
| `Activation Status` | `designed`, `awaiting_manual_paste`, `active`, `paused`, `retired`, `unknown_existing` |
| `Activation Mode` | `agent_self_schedule`, `user_manual_paste`, `external_runtime`, `documented_only` |
| `Execution Mode` | `incremental`, `full_rebuild`, `audit_only` |
| `State Owner` | `project_local`, `registry`, `external_runtime`, `none` |
| `Catch Up Policy` | `cheap_window_only`, `catch_up_when_awake`, `skip_if_stale`, `manual_review` |
| `Retry Policy` | `retry_until_success`, `retry_3_times`, `no_retry`, `manual_review` |
| `Preferred Window` | `midnight_credit`, `morning_review`, `business_hours`, `anytime` |
| `Credit Policy` | `prefer_midnight_5h_cap`, `normal`, `no_ai_credit` |
| `Side Effect Level` | `read_only`, `writes_local`, `writes_external`, `publishes`, `financial` |

## Root Alias Contract

The runtime UI project label is **not** the execution root. A card must carry an exact `Execution Root` — either an absolute path or a `{ALIAS}` defined in your own alias table — and `Root Alias` must equal the alias used at the start of `Execution Root`.

For example, `Execution Root: {PROJECT_ROOT}` requires `Root Alias: PROJECT_ROOT`. The validator enforces this.

## Copyable Example

Copy this card, change the values, keep the field names. It passes `validate_cadence_card.py` as written.

### `CAD-20260101-example-digest` - Example Nightly Digest

| Field | Value |
|---|---|
| Status | `active` |
| Activation Status | `active` |
| Activation Mode | `external_runtime` |
| Created | `2026-01-01` |
| Updated | `2026-01-01` |
| Created By | `You` |
| Planned By | `You` |
| Project Ref | `Example project — nightly digest` |
| Execution Root | `{PROJECT_ROOT}` |
| Root Alias | `PROJECT_ROOT` |
| Runtime Project Label | `My Project` |
| Primary Runtime | `antigravity` |
| Runtime Systems | `antigravity, local scripts` |
| Schedule Frequency | `daily` |
| Schedule Expression | `Daily around 2:30 AM` |
| Timezone | `Asia/Bangkok` |
| Preferred Window | `midnight_credit` |
| Credit Policy | `prefer_midnight_5h_cap` |
| Catch Up Policy | `cheap_window_only` |
| Retry Policy | `retry_until_success` |
| Retry Interval Minutes | `60` |
| Max Catch Up Age Hours | `24` |
| Execution Mode | `incremental` |
| State Owner | `project_local` |
| Checkpoint Path | `.run/cadence/CAD-20260101-example-digest/state.json` |
| Success Marker Pattern | `.run/cadence/CAD-20260101-example-digest/YYYY-MM-DD.success` |
| Resume Policy | `resume_from_checkpoint` |
| Stop Condition | `no new inputs since last_success_at` |
| Output Owner | `reports/nightly-digest.md` |
| Side Effect Level | `writes_local` |
| Requires Human Review | `false` |
| Network Required | `false` |
| Manual Paste Required | `false` |
| Manual Paste Payload | `not_required_config_enabled_project_bound` |
| Source Refs | `predecessor: none; runtime: ~/.gemini/config/sidecars/example-digest/sidecar.json` |

### Saved Prompt (kept with the card)

```text
Project label: My Project
Working directory: /absolute/path/to/your/project

Run the nightly digest.

1. cd "/absolute/path/to/your/project".
2. Read this cadence card and the project instructions.
3. Read .run/cadence/CAD-20260101-example-digest/state.json and the latest success marker.
4. Process only inputs changed since last_success_at. If nothing changed, write a short no-op receipt and stop.
5. Update reports/nightly-digest.md first.
6. Write .run/cadence/CAD-20260101-example-digest/<today>.success only after the report is safely updated.

Keep the response concise.
```
