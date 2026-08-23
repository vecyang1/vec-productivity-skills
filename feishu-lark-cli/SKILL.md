---
name: feishu-lark-cli
description: Use when operating Feishu or Lark through the official lark-cli — searching, reading, or editing Docs, Base, Sheets, Wiki, and Drive — or when diagnosing a Base custom Block tenant/permission error and deciding whether a Block release belongs to the CLI workflow at all.
license: MIT
---

# Feishu / Lark CLI Operator

Use the official `lark-cli` as the primary tool. Do not hand-roll REST calls
until the CLI's own embedded skill and API schema have been checked.

Two habits do most of the work here:

- **The CLI ships its own documentation, version-matched.** `lark-cli skills`
  reads guidance embedded in the binary at build time. Prefer it over any
  local copy — including this one — when the two disagree about flags.
- **Block and tenant errors are identity questions, not artifact questions.**
  They get answered by comparing tenant, workspace, and app owner, not by
  re-uploading a build. Refusing that shortcut is most of this skill.

## Requirements

- Node.js 18+ with a working `npx`.
- The official CLI: `npm install -g @larksuite/cli`, or invoke it per-run with
  `npx --yes @larksuite/cli`. Both expose the `lark-cli` command surface.
- A Feishu (`feishu.cn`) or Lark (`larksuite.com`) account, plus a Developer
  Console app when you need bot identity or a custom Base extension.

## First Checks

1. Run `lark-cli doctor`. If config is missing, use `lark-cli config init --new`
   and pass the returned URL to the user exactly as printed.
   - Inside an agent workspace (`OPENCLAW_HOME` / `HERMES_HOME` set) `config
     init` refuses by default. Use `lark-cli config bind` to bind to the
     workspace's existing app rather than creating a parallel one; only pass
     `--force-init` if the user explicitly wants a separate app.
2. For personal docs or Drive resources, use user identity: `--as user`.
3. For destructive writes, run the command with `--dry-run` first. High-risk
   writes are gated: without `--yes` the CLI exits `10` and returns a
   structured stderr envelope with `error.type == "confirmation"` and
   `error.subtype == "confirmation_required"`. Ask for explicit approval, then
   retry with `--yes` appended to the original argv.
   - Never auto-retry an exit `10` with `--yes`. That disables the gate.
4. Read the shared conventions before any auth, scope, identity, or permission
   work: `lark-cli skills read lark-shared`.
5. If a custom Block reports `You do not have permissions to access the
   internal features of other enterprises`, classify the person before changing
   a release: a same-tenant member in the wrong workspace, or a true
   external-tenant user. These have different fixes, and only one of them is
   reachable from your side.
6. For a Base record-detail Block, do not treat an empty Feishu Admin
   `Workplace → App Management` list as evidence that the Block is uninstalled.
   Verify the target Base runtime and the Block's Developer Console instead.
7. Before saying a Block is available to "all users," compare the target Base
   workspace, the current Admin tenant, and the Developer Console app
   owner/role. "All users" applies only inside the tenant of the released app;
   a Console `403` is an unresolved tenant-or-developer-role gate, not proof
   that inviting another member will fix it.

## Auth Baselines

- Docs-focused setup:
  `lark-cli auth login --domain docs,drive,wiki,base,sheets --scope "search:docs:read"`.
- Full workspace setup: `lark-cli auth login --domain all`. If the tenant
  withholds one specialized scope, keep the granted scopes and continue unless
  the current task needs that exact scope.
- `--domain` accepts a comma-separated list; run `lark-cli auth login --help`
  for the domain vocabulary your CLI version actually supports rather than
  assuming this list is current.
- `auth login` blocks until the user authorizes in a browser. In an agent
  harness that only delivers final turn messages, use `--no-wait --json`, send
  the verification URL (or `lark-cli auth qrcode`) as your final message, then
  complete with `--device-code` on a later turn.
- After auth, verify with `lark-cli doctor`, `lark-cli auth status`, and one
  live read-only command such as
  `lark-cli drive +search --as user --query "" --page-size 5`.
- Bot identity and user identity see different things. A bot cannot read a
  user's private docs unless those docs are shared with the bot.

## Routing

The CLI embeds a per-surface skill for each domain. Read the matching one
before choosing flags — for `docs` the CLI states this as a requirement, not a
suggestion.

| User intent | Command family | Embedded guide |
| --- | --- | --- |
| Search or inspect docs, folders, wiki links, permissions, comments, imports/exports | `lark-cli drive ...` | `skills read lark-drive` |
| Read, create, or edit Feishu Docs / Docx | `lark-cli docs ...` | `skills read lark-doc` |
| Native Markdown files in Drive | `lark-cli markdown ...` | `skills read lark-markdown` |
| Base / bitable tables, fields, views, dashboards, records | `lark-cli base ...` | `skills read lark-base` |
| Spreadsheets | `lark-cli sheets ...` | `skills read lark-sheets` |
| Wiki spaces and nodes | `lark-cli wiki ...` | `skills read lark-wiki` |
| Auth, scope, identity, exit-code conventions | — | `skills read lark-shared` |
| Generic missing shortcut | `lark-cli schema <service>.<resource>.<method>`, then `lark-cli api ...` | `skills read lark-openapi-explorer` |
| Custom Base record-view extension / Block artifact release | Not this CLI. Use the extension project's own release runbook and the official `@lark-opdev/cli`; use `lark-cli base ...` only for Base targeting and post-save readback | — |
| Shared Base opens but its custom Block reports `internal features of other enterprises` | Not an upload defect. Compare the target Base workspace, the current Admin tenant, and the Developer Console app owner/role. Same-tenant users must switch to the app-owning workspace and hold application/Base access; true external-tenant users cannot be enabled by re-sharing the Base and need a Store App decision or an internal-operator workflow | — |

Use `lark-cli skills list` for the full set your version ships, and prefer a
`+shortcut` over a raw API resource whenever one matches the task.

## Docs Defaults

- Discover files with
  `lark-cli drive +search --as user --query "<text>" --format table`.
  `--page-size` accepts 1–20. `--query` is capped at 30 Unicode code points;
  longer queries are rejected server-side.
- Read docs with
  `lark-cli docs +fetch --as user --doc "<url-or-token>"`.
- For edits, fetch with `--detail with-ids` or `--detail full` first, then use
  `docs +update`. `--detail simple` is the default and omits the block ids that
  every targeted edit needs.
- If fetched content contains embedded sheets or bitables, extract their tokens
  and switch to the `sheets` or `base` command family. Do not summarize only
  the embedding tag — it is a pointer, not the content.

### On `--api-version`

Older guidance for this CLI insisted that `docs +create`, `docs +fetch`, and
`docs +update` must carry `--api-version v2`. **Verify before repeating it.**
On current builds the flag is accepted but inert: passing `--api-version v2`
produces a byte-identical `--dry-run` payload and the same resolved endpoint as
omitting it. It is a hidden legacy flag, not a required one.

This is the failure mode worth internalizing beyond this one flag. The CLI
rejects genuinely unknown flags with exit `2` and a `validation` envelope, so
"it didn't error" proves the flag *parses* — never that it *did* anything. To
tell an honoured flag from an ignored one, run `--dry-run` with and without it
and diff the payload. A flag that changes nothing is documentation debt.

## Handling Command Output

- `--dry-run` output embeds the caller's identity context, including `app_id`
  and `user_open_id`. Treat those as account identifiers: do not paste raw
  dry-run payloads into public issues, gists, screenshots, or transcripts.
  Redact them, or report only the resolved `method` and `url`.
- Do not print app secrets, access tokens, OAuth payloads, or raw credential
  files — not in logs, not in transcripts, not while debugging config.
- `lark-cli config init --app-secret-stdin` exists specifically so a secret
  never reaches the process list. Prefer it over any flag that takes a secret
  as an argument.

## Common Mistakes

- Bot identity cannot see the user's private docs unless those docs are shared
  with the bot.
- Wiki URL tokens often need `drive +inspect` to resolve the real object token.
- Inferring docs workflows from `--help` alone. The `docs` domain explicitly
  directs agents to `lark-cli skills read lark-doc` first, and the XML/Markdown
  `--content` rules for `docs +update` live only in its reference files.
- Treating Base records, views, or dashboard blocks managed through
  `lark-cli base` as the release surface for a custom record-view extension.
  Its artifact upload and Developer Console release are a separate
  `@lark-opdev/cli` lifecycle owned by that extension's project; use
  `lark-cli base` for targeting and acceptance readback only.
- Diagnosing `internal features of other enterprises` by re-uploading or
  re-releasing a Block. An enterprise self-built Block stays inside its owning
  tenant even when its Base is shared. Resolve workspace/tenant identity first,
  then choose either internal membership or a multi-tenant Store App path.
- Conflating the Admin Workplace installed-app catalog with a custom Base
  record-view Block. Use that exact Block's Developer Console plus the target
  Base runtime. "All users" does not cross tenants, and a `403` Console page is
  an app-owner or developer-role problem to resolve before onboarding members
  as a purported fix.

## Troubleshooting

Broken `lark-cli` executable, broken `npx` shim after a Node upgrade, and
sandboxed-runtime execution failures: See [troubleshooting.md](references/troubleshooting.md).
