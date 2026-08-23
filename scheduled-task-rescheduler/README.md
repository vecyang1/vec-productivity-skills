# Scheduled Task Rescheduler

Safely **reschedule, rename, rebuild, split, or merge** recurring AI-agent tasks without losing their history or state — across Antigravity, Codex, Claude Code, LaunchAgent, cron, and n8n.

The premise: a scheduler trigger is just an alarm clock. The durable **cadence card** (a Markdown record you own) is the source of truth for why a task exists, where it runs, what it runs, how it catches up, and when it stops. This skill keeps that record honest when schedules change.

## Why This Exists

Editing a recurring task directly in a runtime UI is how you lose track of it. The new time works, but the old checkpoint, the success-marker pattern, the real execution folder, and the *reason* for the change all evaporate. The next run (or the next agent) starts from zero or double-writes. This skill encodes the discipline that prevents that.

## Features

- **Lineage-preserving reschedules** — a checklist + worked examples for rename, new-ID, split, merge, and runtime swaps.
- **Incremental-by-default loop** — read checkpoint → detect changes → no-op or resume → update owner → write success marker last.
- **Antigravity two-layer activation** — the `sidecar.json` + `config.json` + `projects/<id>.json` triangle that must agree before a task is truly active, plus verification and pause/retire steps.
- **Deliberate catch-up & credit policy** — `cheap_window_only` for expensive midnight jobs so a missed 2 AM run can't burn daytime credit; `catch_up_when_awake` when lateness is still useful.
- **Copy-paste cadence-card template** with full field and status vocabulary.
- **Zero-dependency validator** — `scripts/validate_cadence_card.py` checks required fields, status vocab, incremental-state completeness, and alias↔root agreement.

## Use Cases

- Moving a nightly job to a new time without orphaning its checkpoint.
- Splitting one bloated recurring task into two, or merging two into one.
- Activating an Antigravity scheduled task by writing config directly (not just pasting in the UI).
- Deciding whether a missed run should catch up or be skipped.
- Auditing a pile of existing scheduled tasks into clean, reviewable records.

## Quick Start

1. Read [`SKILL.md`](SKILL.md) — the model and the rules.
2. Copy [`references/cadence-card-template.md`](references/cadence-card-template.md) into your repo/vault and fill one card per recurring task.
3. Validate:
   ```bash
   python3 scripts/validate_cadence_card.py path/to/your-cadence-records.md --strict
   ```
4. Point your runtime (Antigravity / cron / LaunchAgent / n8n) at the execution root in the card. For Antigravity, follow [`references/antigravity-activation.md`](references/antigravity-activation.md).

## Files

```
scheduled-task-rescheduler/
├── SKILL.md                              # the skill: model, rules, checklist
├── README.md                             # this file
├── references/
│   ├── reschedule-lineage.md             # preserve the track on reschedule/rename/split/merge
│   ├── antigravity-activation.md         # two-layer config activation + verification
│   ├── cadence-card-template.md          # copyable record + field & status vocabulary
│   └── catch-up-and-credit.md            # missed-run, retry, and credit-window policy
├── scripts/
│   └── validate_cadence_card.py          # zero-dependency cadence-card validator
└── tests/
    └── test_validate_cadence_card.py     # stdlib unittest suite for the validator
```

## Testing

The validator ships with a dependency-free `unittest` suite (includes a regression guard so card headings inside fenced code blocks are never mis-parsed):

```bash
python3 -m unittest discover -s scheduled-task-rescheduler/tests
```

## License

MIT — see the repository [`LICENSE`](../LICENSE).
