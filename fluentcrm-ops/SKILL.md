---
name: fluentcrm-ops
description: Use when operating FluentCRM on WordPress sites, including CRM contact counts, contacts, tags, lists, automations/funnels, campaigns, REST/PHP API checks, Novamira WordPress MCP bridge access, or refreshing the live FluentCRM command/function surface for future agents.
---

# FluentCRM Ops

Operate FluentCRM as a general WordPress CRM system. Prefer the bundled CLI for repeatable Codex work; it uses the Novamira WordPress MCP/PHP bridge when direct MCP tools are not available in Codex.

## First Move

Run read-only checks before changing CRM state:

```bash
python3 ~/.codex/skills/fluentcrm-ops/scripts/fluentcrm_ops.py doctor
python3 ~/.codex/skills/fluentcrm-ops/scripts/fluentcrm_ops.py counts
```

If the Codex symlink is missing, run from the source skill:

```bash
python3 /path/to/fluentcrm-ops/scripts/fluentcrm_ops.py doctor
```

The CLI inherits Novamira credentials from `WP_API_URL`, `WP_API_USERNAME`, `WP_API_PASSWORD`, local `.env`, or an agent MCP config file. For already-configured WordPress sites, reuse the existing Novamira WordPress connection rather than asking the user to log in again.

## Decision Table

| Task | Use |
|---|---|
| Check plugin/table health | `doctor` |
| Verify the full safe Codex loop | `self-test` |
| Count contacts/lists/tags | `counts` |
| Browse tags, lists, automations | `tags`, `lists`, `funnels` |
| Search contacts | `contacts --search ...` |
| Create/update contact | `upsert-contact` first without `--confirm-write`, then rerun with `--confirm-write` after checking payload |
| Call a known read-only Novamira/FluentCRM ability | `ability <name> --params '{...}'` |
| Inspect new plugin functions/classes/tables | `refresh-surface --output references/live-surface.json` |
| Custom read-only query | `php "return ...;"`; write-like PHP requires `--confirm-write` |

## Safety Rules

- Do not write directly to FluentCRM database tables for contacts, tags, lists, campaigns, or funnels. Use FluentCRM PHP/REST APIs or Novamira `fluent-crm/*` abilities.
- Treat one-off email sends, campaign sends, automation activation, import, bulk edit, and deletion as high-risk. Get explicit user approval and run a dry-run/preview first.
- Do not paste raw contact emails or personal data into chat unless the user asked for those exact records. Prefer counts, IDs, statuses, and summarized findings.
- Tags/lists passed as new strings may create new segmentation objects. Prefer existing IDs/slugs unless creation is intentional.
- Always derive table names from `$wpdb->prefix`; never assume `wp_`.
- Raw `php` and `ability` commands block obvious write-like operations unless `--confirm-write` is supplied. This is a safety backstop, not a substitute for approval on high-risk CRM work.

## CLI Commands

```bash
# Health and counts
python3 scripts/fluentcrm_ops.py doctor
python3 scripts/fluentcrm_ops.py counts
python3 scripts/fluentcrm_ops.py self-test

# Segments and automations
python3 scripts/fluentcrm_ops.py tags --limit 100
python3 scripts/fluentcrm_ops.py lists --limit 100
python3 scripts/fluentcrm_ops.py funnels --limit 50

# Contact search
python3 scripts/fluentcrm_ops.py contacts --search ada@example.com --limit 25
python3 scripts/fluentcrm_ops.py contacts --tag vip --status subscribed

# Safe write preview, then confirmed write
python3 scripts/fluentcrm_ops.py upsert-contact ada@example.com --first-name Ada --tag vip
python3 scripts/fluentcrm_ops.py upsert-contact ada@example.com --first-name Ada --tag vip --confirm-write

# Raw write-capable escape hatches require explicit confirmation
python3 scripts/fluentcrm_ops.py ability fluent-crm/upsert-contact --params '{"email":"ada@example.com"}' --confirm-write

# Keep this skill current after plugin upgrades
python3 scripts/fluentcrm_ops.py refresh-surface --output references/live-surface.json
python3 scripts/fluentcrm_ops.py self-test --refresh-surface
```

## Updating This Skill

When FluentCRM adds or changes functions, endpoints, tables, actions, or benchmarks:

1. Run `refresh-surface --output references/live-surface.json` against the live site.
2. Check `references/fluentcrm-official-surface.md` for current official docs and update it if the docs changed.
3. Add only reusable new commands/gotchas to this `SKILL.md`; put bulky schema/API detail in `references/`.
4. Run the safe E2E and validation checks:
   ```bash
   python3 scripts/fluentcrm_ops.py self-test --refresh-surface
   python3 -m unittest discover -s tests
   python3 /path/to/skill-creator/scripts/quick_validate.py .
   ```

## Gotchas

- The Novamira endpoint is MCP-session based. Do not call `/wp-json/mcp/novamira` directly unless you manage MCP session headers. Use this CLI or `novamira-ops/scripts/wp_ops.py`.
- The CLI unwraps Novamira transport envelopes so commands return the useful FluentCRM payload (`return_value` or `data`) directly. Use `novamira-ops` if you need raw MCP transport debugging.
- Antigravity may expose Novamira as MCP tools, but Codex often only has shell access. The CLI is the stable Codex interface.
- FluentCRM official REST docs are broad and still evolving; the installed plugin is the runtime truth. Refresh the live surface before relying on a newly documented endpoint.
- If FluentCRM is not loaded but tables exist, read-only database checks may still work; writes should stop until plugin health is fixed.

## References

- `scripts/fluentcrm_ops.py`: CLI wrapper.
- `references/fluentcrm-official-surface.md`: official docs and API surface notes.
- `references/fluentcrm-repo-analysis.md`: repository directory structure, key models, and PHP API classes.
- `references/novamira-bridge.md`: bridge setup, credential lookup, and troubleshooting.
