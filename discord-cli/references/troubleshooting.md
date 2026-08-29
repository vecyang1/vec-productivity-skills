# discord-cli Troubleshooting

| Symptom | Safe recovery |
| --- | --- |
| `discord` is not found | Run `discord --help`; install `kabi-discord-cli` with `uv tool install kabi-discord-cli` only if it is missing. |
| `DISCORD_TOKEN not set` or an invalid-session error | Do not run `discord auth --save` and do not ask for a token in chat. Check the approved secret owner and confirm account/server authorization before a process-scoped retry. |
| `discord auth` reports **"No tokens found"** while Discord is clearly logged in | Not a logged-out account, and not a reason to escalate. `auth.py` only regex-scans leveldb `*.ldb`/`*.log` for plaintext; modern Discord encrypts the token at rest via Electron `safeStorage` (key in the macOS Keychain item `discord Safe Storage`), leaving a `dQw4w9WgXcQ`-prefixed blob the scanner cannot read. The command predates that change and now finds nothing on any current client. Get the token from the secret owner instead — see SKILL.md **Credential Lane**. Do not decrypt the Keychain key or capture the token from the app. |
| A channel is inaccessible | Treat the result as an authorization boundary. Do not retry through a different account or broaden the server scan. |
| A channel returns `fetched: 0` but the server is clearly active | Check its `type` in `dc channels`. `type: 15` is a forum: the posts are threads, and `/guilds/{id}/channels` never lists threads. Use `dc search` then `dc history <thread_id>` — see SKILL.md **Forum Channels Are Not Reachable By Channel**. Zero is not evidence of no activity. |
| Large sync or search output | Narrow to a known channel, use `-n`, and search the local cache. Do not use `sync-all` as an automatic fallback. |
| Export is too broad | Re-run with the requested channel and a smaller scope. Do not retain surplus exports. |
| Local cache must be removed | Present the exact channel and use `discord purge CHANNEL -y` only after explicit confirmation. |

Run `discord --help` after an upgrade before relying on a new flag or local-store behavior.

## Structured output contract

Every `--json` / `--yaml` command wraps its result in one envelope. Reading the
envelope as the payload silently reports a healthy account as unauthenticated:

```json
{ "ok": true, "schema_version": "1", "data": <payload> }
{ "ok": false, "schema_version": "1", "error": { "code": "...", "message": "..." } }
```

Unwrap `data` first, then use the per-command shape — they are not uniform, and
a `len()` on the wrong shape reads as zero rather than erroring:

| Command | `data` shape |
| --- | --- |
| `status` | `{"authenticated": bool, "user": {...}}` |
| `whoami` | `{"user": {...}}` — the profile is nested one level deeper |
| `dc guilds`, `dc channels` | list |
| `dc history`, `dc sync` | `{"fetched": N, "stored": M}` — **not** a message list |
| `dc search` | list of message dicts, straight from Discord's server-side search — distinct from top-level `search`, which reads only the local store |
| `stats` | `{"total": N, "channels": [...]}` |
| `search`, `recent`, `top`, `timeline`, `today` | list |

When stdout is not a TTY the CLI already defaults to YAML, so pass `--json`
explicitly if a parser expects JSON.

## Isolating a test run

`scripts/e2e_check.py` already does this; read on only when writing a different
check. `DB_PATH` and `DATA_DIR` (both read by `config.py`) redirect the local
store. Point them at a temp path to exercise sync/search/export/purge without
touching — or being flattered by — an existing cache, and assert against the
sqlite `messages` table rather than trusting command exit codes alone.
`dc history` on an unreadable channel exits non-zero via an uncaught
`raise_for_status`; treat that as the authorization boundary, not a bug to retry
around.

Pick the channel to drive the flow from by **volume, not by position**. The
first channel with any traffic is often near-empty, and a one-message corpus
lets every downstream stage report PASS while exercising nothing: search finds
no term to use, aggregation has nothing to group, paging never triggers. Probe
several channels and drive from the busiest.
