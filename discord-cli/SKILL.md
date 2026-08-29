---
name: discord-cli
description: "Use when operating the kabi-discord-cli Discord command-line tool for authorized server/channel discovery, bounded history sync, local message search, analytics, export, local-cache purges, setup, status, or Discord CLI failures."
---

# discord-cli

## Skill Metadata

- **Origin:** `local`
- **Source:** Adapted from https://github.com/jackwener/discord-cli at `ce32e6b37bdf1a3852ebf65fbdf580ee81361155`
- **Author:** Original CLI: jackwener; adapter: Vec + Codex
- **Created:** 2026-08-10
- **Updated:** 2026-08-29
- **Review status:** `reviewed` — full flow verified live via `scripts/e2e_check.py` on 2026-08-10 (11/11 stages). `scripts/forum_sweep.py` verified live the same day through the no-argv 1Password adapter path: on a 34-channel guild it found 7 forums, discovered **37 threads** that channel-level reads reported as `fetched: 0`, and read two of them in full. Unit suite 8/8 hermetic; 9/9 seeded mutations of its core logic were caught.

## 🔄 Beeper Redirection & Channel Coordination

> [!IMPORTANT]
> **Prefer `beeper-ops` When Beeper is Connected**: If Discord is already bridged into Beeper Desktop (`discordgo` bridge), route normal chat reads, contact discovery, and cross-platform searches to `beeper-ops` first.
> 
> **When to stay in `discord-cli`**:
> 1. **Discord Forum Channels (Type 15)**: Beeper's Discord bridge does not automatically carry forum channels and threads (every post is a thread). For forum sweeps and forum thread exports, use this skill's `forum_sweep.py` or direct Discord queries.
> 2. **Unbridged Discord Servers / Deep Search**: Direct Discord server search across all historical messages.

## Agent Reach Link

Use `agent-reach` for public web and public social research. Use this skill only for authorized Discord account and server data. Do not send private Discord content to Agent Reach; pass only a user-approved, non-sensitive public lead when cross-platform research is actually needed.

## Security Boundary

This upstream CLI uses a Discord user-token API client and can scan local browser or Discord LevelDB storage. Do not run `discord auth --save`; it can extract a token and write it to a local `.env` file. Do not print or persist raw tokens, ask a user to paste one in chat, or treat a Discord user token as a routine browser cookie.

A Discord user token is password-equivalent and automating with one is a self-bot ToS violation. Keep usage bounded and read-only. Decline to extract, decrypt, or capture the token yourself even when the user authorizes it — the supported route is the user placing it in the secret store and the process receiving it by injection.

Before any live call, confirm the account and server scope are authorized. Use a pre-existing, approved secure credential pointer that exposes `DISCORD_TOKEN` only to the process; use `1password` when credential discovery is necessary. If no approved credential path exists, stop and report that access is not configured.

## Credential Lane

`DISCORD_TOKEN` is read from the environment only (`config.py:get_token`), so the whole credential question is "how does the value reach the child process without being seen".

Resolved route on this machine — a 1Password item in the automation vault, injected by the `1password` skill's fixed-command adapter:

```bash
python3 ~/.agents/skills/1password/scripts/unattended_env.py --spec <spec.json>
```

The spec names the `op://` reference and one absolute executable. Three constraints that are easy to get wrong:

- `command` takes **exactly one absolute path and no arguments**. Configure the child through env defaults or a project-owned wrapper, not argv.
- Every `environment` value must be exactly `{{ op://<vault>/<item>/<field> }}`. Literal values are rejected, so a child cannot be configured through that map.
- The adapter **discards child stdout**, so a child must leave its own receipt on disk.

Do not use `op run` for this (the Service Account route disables it), and never satisfy a Touch ID prompt to unblock it — that proves a lane which will not exist when the user is away. The concrete vault/item pointer is agent-local memory, not this skill.

## Verification

Prove the whole flow rather than the login. `discord status` passing only means the token is live; it says nothing about channel access, the local store, or search.

```bash
python3 scripts/e2e_check.py          # needs DISCORD_TOKEN in the environment
```

Exercises status → whoami → guilds → channels → history → local store → sync → search → stats/recent/top/timeline/today → export → purge, against a temp `DB_PATH` so it can neither pollute nor be flattered by the real cache. The receipt records counts and shapes only, never message bodies or sender names. Zero-arg by design so the fixed-command adapter can run it; receipt defaults to `~/.cache/discord-cli-e2e/e2e.out` (override with `--sink` or `DISCORD_E2E_SINK`), echoed to stdout only when stdout is a terminal.

Run it after a token rotation, a `kabi-discord-cli` upgrade, or on a new machine. It is also what catches upstream payload-shape drift, since it exercises the shapes the reference documents.

## Preflight

```bash
discord --help
discord status --yaml
```

If the binary is absent, install the maintained package:

```bash
uv tool install kabi-discord-cli
```

## Bounded Local-First Workflow

The CLI stores synced message data locally. Keep requests specific and small, then use local search rather than repeatedly re-fetching a server:

```bash
discord dc guilds --yaml
discord dc channels GUILD_ID --yaml
discord dc history CHANNEL_ID -n 100 --yaml
discord search "keyword" -c CHANNEL_NAME --yaml
discord today -c CHANNEL_NAME --yaml
```

Use `discord dc sync CHANNEL_ID` for a known channel; do not use `sync-all` unless the user explicitly asks for that scope. Export only the requested channel, time range, and format, then return the output path and data-scope receipt.

Before parsing `--json`/`--yaml` output, read the payload-shape table in [troubleshooting.md](references/troubleshooting.md): every command wraps its result in an `{ok, schema_version, data}` envelope and the per-command shapes are not uniform. Both mistakes fail silently as a false negative — a healthy account reads as `authenticated=False`, a busy channel reads as zero messages — so they get misattributed to the token or to permissions.

## Forum Channels Are Not Reachable By Channel

`dc channels` is backed by `/guilds/{id}/channels`, which does not return threads.
A **forum channel** (`type: 15` in that output) holds no linear messages — every
post is its own thread — so `dc history <forum_id>` returns `fetched: 0`. It does
not error. A server's busiest support channel therefore renders as empty, and the
absence gets read as "the community is quiet".

Reach the content in two steps, both already in the CLI:

```bash
discord dc search GUILD_ID "keyword" -n 25   # server-side; DOES index threads
discord dc history THREAD_ID -n 50           # a thread is a channel
```

`scripts/forum_sweep.py` packages both steps, isolates the local store, and
withholds message bodies unless `--include-text` is passed:

```bash
python3 scripts/forum_sweep.py --guild GUILD_ID --query selector --query bug --threads 3
```

With no arguments it reads `./forum_sweep.config.json`, so the fixed-command
1Password adapter — which passes no argv and discards stdout — can drive it.

`dc search` (Discord's `/guilds/{id}/messages/search`) is a different command
from top-level `search`, which only queries the local SQLite store. The name
collision is easy to miss and the local one cannot see anything never synced.

Identify thread hits by `channel_id`: any hit whose channel id is absent from the
`dc channels` set came from a thread. Discovery is keyword-bound — there is no
list-all-threads command, because `/guilds/{id}/threads/active` is not wrapped.

Read `type` before concluding anything from an empty channel. Measured on one
server: 13 of 34 channels carried linear messages, 7 were forums, and a release
that shipped six weeks earlier existed only inside forum threads while the
announcement channel showed nothing newer than the prior version. A four-keyword
sweep of that same server surfaced 37 threads the channel-level read had scored
as zero.

Because discovery is keyword-bound, a sweep's silence is never proof of absence:
report which keywords were used, and treat an unreached forum as unsearched.

## State Changes

Syncing creates or updates a local message cache. `discord purge CHANNEL` deletes locally stored data. Before a purge, show the exact channel and local effect, obtain explicit user confirmation, then run one purge. Never infer permission to purge from permission to read or export.

## Troubleshooting

Resolving common issues: See [troubleshooting.md](references/troubleshooting.md).

## Sources

- https://github.com/jackwener/discord-cli
- https://github.com/jackwener/discord-cli/blob/main/SCHEMA.md
