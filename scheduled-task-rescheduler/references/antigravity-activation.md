# Antigravity: Two-Layer Activation

An Antigravity scheduled task is **not** active just because a sidecar file exists on disk. Activation lives in two layers — the sidecar definition and the runtime config that enables and binds it — across three files that must agree.

> Field names and exact layout can vary by Antigravity / Gemini CLI version. The shapes below are illustrative. Always read your actual installed files and match what is already there rather than overwriting blindly.

## The Three Files

| File | Owns |
|---|---|
| `~/.gemini/config/sidecars/<slug>/sidecar.json` | schedule, display name, command, saved prompt |
| `~/.gemini/config/config.json` → `sidecars.<slug>` | `enabled` flag and `projectId` binding |
| `~/.gemini/config/projects/<projectId>.json` | UI project label and the real folder URI |

### 1. Sidecar definition — `sidecars/<slug>/sidecar.json`

Holds the schedule, the display name, and the saved prompt. The prompt **must** contain an explicit `cd` to the absolute execution root:

```jsonc
{
  "displayName": "My Project — Nightly Digest",
  "schedule": "Daily around 2:30 AM",
  "command": "<the agent command the runtime invokes>",
  "prompt": "cd \"/absolute/path/to/your/project\"\n\nRun the nightly digest. Read the cadence card, read the checkpoint, process only changed inputs, update the report, then write the success marker."
}
```

### 2. Enable + bind — `config.json`

A sidecar only fires when it is enabled **and** bound to a project:

```jsonc
{
  "sidecars": {
    "<slug>": {
      "enabled": true,
      "projectId": "<PROJECT_ID>"
    }
  }
}
```

### 3. Project mapping — `projects/<PROJECT_ID>.json`

Maps the human-facing UI label to the real folder URI:

```jsonc
{
  "label": "My Project",
  "uri": "file:///absolute/path/to/your/project"
}
```

## The Label Is Not The Root

The UI project label is **only a label**. The Antigravity project dropdown can be broader than the folder where the task should actually run. So:

- The cadence card's `Execution Root` and the prompt's `cd` / `Working directory:` must use the **real absolute folder path**.
- Quote the project label in the prompt only as a human hint, never as the execution contract.

## Two Activation Paths

### Manual paste (UI)

A human or agent creates the task in the Antigravity UI. Until paste is confirmed, the cadence card stays `Activation Status: awaiting_manual_paste` with a paste-ready payload that includes:

- **Name**
- **Project dropdown label**
- **Schedule**
- **Prompt** (with the explicit `cd`)

### Direct config

An agent writes all three files above, then **verifies** before claiming the task is active.

## Verification Gate

After direct-config activation (or any edit), confirm all of the following for an active task:

1. the sidecar file exists and has a non-empty prompt;
2. `config.json` has `sidecars.<slug>.enabled = true`;
3. `sidecars.<slug>.projectId` points to a project file that exists;
4. that project's folder URI **covers** the execution root in the cadence card;
5. the UI label matches the project file's label;
6. the prompt is rooted — it contains a `cd "<execution root>"` matching the card.

For **paused / retired** tasks, the inverse must hold: the runtime sidecar must **not** still be `enabled`. An enabled sidecar with no owning cadence card, or a retired card whose sidecar is still enabled, is drift — catch it in review.

## Pause / Retire Cleanly

- **Pause:** set `enabled: false` in `config.json`; set the card `Status: paused`, `Activation Status: paused`. Keep the sidecar file and checkpoint so you can resume.
- **Retire:** set `enabled: false`; set the card `Status: retired`; keep the card (and its `Source Refs`) for lineage. Remove the sidecar only once nothing references it.

## Audit Idea

A tiny watchdog job can run a strict check daily: enabled sidecars must each map to an `active` cadence card that is project-bound, label-matched, and prompt-rooted; paused/retired cards must not be enabled. Report drift instead of mutating sidecars automatically — a watchdog that silently rewrites runtime config is its own failure mode.
