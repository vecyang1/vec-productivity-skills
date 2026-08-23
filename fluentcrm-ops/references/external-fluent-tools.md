# External Fluent Tools

Use this file before extending `fluentcrm-ops` with new MCP-style tools or automation trigger behavior. It records third-party patterns to learn from without making them the source of truth.

Last checked: 2026-06-21.

## carlosrodera/fluent-mcp-servers

- Repository: https://github.com/carlosrodera/fluent-mcp-servers
- License: MIT.
- Relevant package: `fluent-crm-mcp`.
- Shape: TypeScript MCP server over the FluentCRM REST API at `/wp-json/fluent-crm/v2/`.
- Auth/config pattern: WordPress Application Passwords via `FLUENTCRM_URL`, `FLUENTCRM_USERNAME`, `FLUENTCRM_APP_PASSWORD`, with optional config file support.
- Tool surface observed: 40 FluentCRM tools across contacts, tags, lists, campaigns, templates, sequences, funnels, reports, and webhooks.
- Useful design pattern: dynamic mode exposes only `fluentcrm_search_tools`, `fluentcrm_describe_tools`, and `fluentcrm_execute_tool` so agents can discover and call tools without loading the full tool schema into context.
- Useful safety pattern: tool annotations distinguish read-only, idempotent, and destructive operations. Mirror this idea in CLI docs and write gates before adding new commands.

How to use the learning:

- Use it as a REST/MCP endpoint taxonomy checklist when Novamira abilities are missing.
- Consider adding a future `rest` subcommand only if the local site has stable application-password credentials and the same operation is repeated often.
- Do not replace the Novamira bridge by default; for this skill, the installed plugin plus `refresh-surface` remains runtime truth.

## verygoodplugins/fluent-crm-field-updated-trigger

- Repository: https://github.com/verygoodplugins/fluent-crm-field-updated-trigger
- License: GPL-3.0.
- Purpose: adds FluentCRM funnel triggers when a standard contact field or custom contact field changes.
- Boot pattern: waits for `fluentcrm_loaded` before registering trigger classes.
- Trigger names observed:
  - `fluentcrm_contact_custom_data_updated`
  - `fluentcrm_contact_updated`
- Funnel settings/conditions worth remembering:
  - `field_name` selects the watched standard/custom field.
  - `update_type` supports `any` or `specific`.
  - `field_value` holds the exact value for `specific` matching.
  - `field_empty` can skip empty updates; release `1.2.0` added this behavior even though the plugin header still reports `1.1.0`.
  - `run_multiple` controls whether an already-enrolled contact can restart the automation.
- Process pattern: check whether the updated field/value is processable, apply `fluentcrm_funnel_will_process_{triggerName}`, then start the funnel sequence with `source_trigger_name`.

How to use the learning:

- When a user asks for a field-change automation, inspect installed trigger classes and funnel trigger names before inventing custom SQL or brittle polling.
- Treat this as conceptual reference only. Do not copy GPL source into this MIT/community skill or public mirror.
- If implementing comparable behavior on a private WordPress site, prefer a small site-owned plugin that registers a `BaseTrigger` after `fluentcrm_loaded`, then validate against a staging contact before activation.
