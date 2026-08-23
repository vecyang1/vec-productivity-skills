# FluentCRM Official Surface

Use this file when deciding whether to use database reads, PHP API, REST API, or Novamira abilities.

## Current Official Sources & Codebase

Last checked against the official developer docs on 2026-06-21. Treat the installed plugin and `refresh-surface` output as runtime truth when docs and live code differ.

- Upstream repository: https://github.com/FluentCRM/fluent-crm
- Local analysis reference: `references/fluentcrm-repo-analysis.md`
- Developer getting started: https://developers.fluentcrm.com/getting-started/
- Database schema: https://developers.fluentcrm.com/database/
- REST API overview: https://developers.fluentcrm.com/rest-api/
- REST authentication: https://developers.fluentcrm.com/rest-api/authentication
- Contacts PHP API: https://developers.fluentcrm.com/global-functions/contact-api-function

## Stable Concepts

- Contacts are subscribers and live around the `fc_subscribers` model/table.
- Segmentation uses `fc_tags` and `fc_lists`.
- Automations are funnels. The core automation pieces are triggers, actions, and benchmarks.
- Campaigns, templates, reports, dynamic segments, webhooks, settings, imports, users, forms, migrators, and abandon carts have REST modules.
- Official REST API requests can permanently change data. Use test/staging or dry-run/preview when possible.

## Database Tables Commonly Needed

Always prepend `$wpdb->prefix`; never hardcode `wp_`.

| Table suffix | Purpose |
|---|---|
| `fc_subscribers` | Contact/subscriber records |
| `fc_tags` | Segment tags |
| `fc_lists` | Mailing lists |
| `fc_subscriber_pivot` | Subscriber relationship pivot |
| `fc_funnels` | Automation workflows |
| `fc_funnel_sequences` | Automation steps |
| `fc_campaigns` | Broadcast campaigns |
| `fc_campaign_emails` | Per-contact campaign emails |
| `fc_meta` | Shared key-value metadata |
| `fc_subscriber_notes` | Contact notes/activity |
| `fc_companies` | Company records |

## Write Strategy

Prefer API/model operations over direct SQL:

- Contact create/update: `FluentCrmApi('contacts')->createOrUpdate(...)` or Novamira `fluent-crm/upsert-contact`.
- Tag/list attach/detach: Subscriber methods such as `attachTags`, `detachTags`, `attachLists`, `detachLists`, or the equivalent REST/ability.
- REST authentication should use WordPress/FluentCRM manager credentials or application passwords. Avoid admin credentials for durable integrations.

## Live Surface Refresh

Run this after plugin upgrades or when an agent discovers a missing function:

```bash
python3 scripts/fluentcrm_ops.py refresh-surface --output references/live-surface.json
```

Review the generated `plugin_surface` section for new PHP classes under:

- `app/Services/Funnel/Actions`
- `app/Services/Funnel/Benchmarks`
- `app/Http/Controllers`
- `app/Models`
