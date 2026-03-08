---
name: clawdbot-repair
description: Expert guide for troubleshooting and repairing Clawdbot installations. Use this skill when Clawdbot is not working, the agent is missing from the UI, or there are connection/authentication errors.
---

# Clawdbot Repair & Troubleshooting

This skill encapsulates the knowledge required to fix common Clawdbot issues, including visibility problems, authentication failures, and process conflicts.

## 1. Quick Diagnostics

Run the doctor command to identify basic configuration and permission issues:

```bash
clawdbot doctor
```

If it reports issues, try the auto-fix:

```bash
clawdbot doctor --fix
```

## 2. Starting Clawdbot

There is no `clawdbot start` command. Use one of these methods:

**Method A: The Correct Command**
```bash
clawdbot gateway
```

**Method B: Helper Script (Recommended)**
If you have the `start_clawdbot.sh` script:
```bash
./start_clawdbot.sh
```
*(This script runs `clawdbot gateway --force` to handle any cleanup automatically)*

**Method C: 'start' Alias (User Specific)**
You have an alias set up so you can just run:
```bash
start
```
*(This triggers Method B)*

## 3. Common Issues & Fixes

### A. Main Agent Missing from UI

**Symptoms:**
- You can access `http://127.0.0.1:18789` but the dropdown is empty or missing "main".
- `clawdbot sessions list` shows the session exists but it's not in the UI.

**Cause:**
The session might be incorrectly tagged with a hidden channel (e.g., `whatsapp`).

**Fix:**
1. Edit the session file: `~/.clawdbot/agents/main/sessions/sessions.json`
2. Look for existing sessions (e.g., `agent:main:main`).
3. **Remove** or **Change** the `"channel": "whatsapp"` line. It should be `"channel": "webchat"` or removed (defaults to webchat/direct).
4. Restart the gateway (see Section C).

### B. Authentication Errors (Token Reused / Missing)

**Symptoms:**
- `clawdbot doctor` shows `[openai-codex] Token refresh failed: ... refresh_token_reused`.
- Agent hangs when sending messages via CLI.

**Fix:**
Refresh the authentication token:

```bash
codex login
```

After logging in, you **must** restart the gateway for the new token to take effect.

### C. Gateway & Process Conflicts (Connection Refused / HTTP 500)

**Symptoms:**
- `http://127.0.0.1:18789` returns `ERR_CONNECTION_REFUSED`.
- `clawdbot gateway` fails to start saying "port already in use" or "lock timeout".

**Fix:**
Forcefully kill old processes and start a clean gateway:

```bash
# 1. Kill existing processes
pkill -f clawdbot

# 2. Start gateway cleanly (and force kill port hogs)
clawdbot gateway --force
```

### D. Gateway Crashing Immediately (Slack/Socket Error)

**Symptoms:**
- You try to start the gateway, but it stops after a few seconds.
- Logs (`/tmp/clawdbot.log`) show `Client network socket disconnected` or Slack errors.

**Fix:**
Disable the Slack integration in the config, as it often causes unstable boots if the token is invalid.

1. Open `~/.clawdbot/clawdbot.json`.
2. Find `channels` -> `slack`.
3. Set `"enabled": false`.
4. Restart gateway.

**Adding Missing Scopes (`chat:write`):**
1. Go to **Features** > **OAuth & Permissions** (NOT "Event Subscriptions").
2. Scroll down to **Scopes** > **Bot Token Scopes**.
3. Click **Add an OAuth Scope** and search for `chat:write`.
4. Scroll back to top and click **Reinstall to Workspace**.
5. Update `clawdbot.json` with the new `botToken`.

### E. UI Authorization (Token Missing)

**Symptoms:**
- UI Loads but shows "Disconnected" or console errors about `unauthorized`.
- Logs show `reason=token_missing`.

**Fix:**
You must use the **Tokenized URL** to access the UI.

1. Get the token from config:
   ```bash
   cat ~/.clawdbot/clawdbot.json | grep gatewayToken
   ```
2. Construct URL: `http://127.0.0.1:18789/?token=<YOUR_TOKEN>`

### F. Switching AI Models (Google <-> OpenAI)

**Scenario:**
You want to switch from Google Gemini back to OpenAI (ChatGPT web login) or vice versa.

**Fix:**
Run the onboard wizard:
```bash
clawdbot onboard
```
1. Select **configure agents**.
2. Select **default**.
3. Choose your desired provider (e.g., `openai-codex`).
4. If asked to authenticate, run `codex login`.
5. **Restart the gateway** for changes to take effect (`./start_clawdbot.sh`).

### G. WhatsApp Pairing

**Scenario:**
You see a message: `Clawdbot: access not configured... Pairing code: XXXXX`.

**Fix:**
This happens when a new WhatsApp number contacts the bot. The code is temporary (valid until restart).
1. Copy the pairing code from WhatsApp.
2. Run the approval command:
   ```bash
   clawdbot pairing approve whatsapp <CODE>
   ```
   *(Example: `clawdbot pairing approve whatsapp YOUR_PAIRING_CODE`)*
3. If it says "No pending request", the code expired or the gateway restarted. Just message "hi" on WhatsApp again to get a new code.

### H. Security: Who can talk to my bot?

**Default Policy: Allowlist Only**
By default, Clawdbot is **Private**.
- Strangers who message your bot number **will NOT** get an AI reply.
- Instead, they will trigger a "Pairing Request" (the code).
- Unless you run `clawdbot pairing approve ...`, the bot ignores them.
- **You** created the connection by approving your own number, so only you (and anyone else you explicitly approve) can chat.

## 3. Verification

To verify the agent is working:

1. **CLI Check:**
   ```bash
   clawdbot agent --to main --message "Hello test" --deliver
   ```
2. **UI Check:**
   Open the tokenized URL in Chrome.

## 4. Useful Paths

- **Config**: `~/.clawdbot/clawdbot.json`
- **Session Store**: `~/.clawdbot/agents/main/sessions/sessions.json`
- **Logs**: `/tmp/clawdbot.log` (or `clawdbot-*.log`) and `~/.clawdbot/logs/gateway.log`

## 6. Gateway LaunchAgent (macOS — CRITICAL)

OpenClaw on macOS is managed by a LaunchAgent (`ai.openclaw.gateway`). **Never use `openclaw gateway --force` manually** — the LaunchAgent owns the process and will immediately SIGTERM any manually started gateway.

**Correct restart:**
```bash
launchctl unload ~/Library/LaunchAgents/ai.openclaw.gateway.plist
launchctl load ~/Library/LaunchAgents/ai.openclaw.gateway.plist
```

Or if the LaunchAgent got unloaded (shows `-` in `launchctl list`):
```bash
launchctl load ~/Library/LaunchAgents/ai.openclaw.gateway.plist
```

Verify: `openclaw health` — should show Telegram/Slack ok.

## 7. Model Fallback Chain (openai-codex → google-antigravity)

**VPS bots**: Antigravity as primary (avoids token race), openai-codex as fallback. See §10.
**Local Mac**: openai-codex as primary, google-antigravity as fallback.

```bash
# View current fallbacks
openclaw models fallbacks list

# Add fallback
openclaw models fallbacks add google-antigravity/gemini-3-pro-high

# Swap to 3.1 once available
openclaw models fallbacks remove google-antigravity/gemini-3-pro-high
openclaw models fallbacks add google-antigravity/gemini-3.1-pro
```

**Note:** `google-antigravity/gemini-3.1-pro` requires Antigravity Tools.app to be running AND updated. Check version: `mdls -name kMDItemVersion /Applications/Antigravity\ Tools.app`. As of 2026-03-01, v4.1.26 only exposes up to `gemini-3-pro-high` locally.

**IMPORTANT (2026-03-01):** The Antigravity API server has deprecated `gemini-3-pro-high` — it returns "Gemini 3 Pro is no longer available. Please switch to Gemini 3.1 Pro." Both VPS bots AND local Mac must use `gemini-3.1-pro`. The Antigravity Tools.app proxy no longer shields local Mac from this deprecation. Use `gemini-3.1-pro` everywhere.

**Fallback behavior (normal):** Bots may respond with "(Note: I'm currently running on gemini-3-flash, but my default is gemini-3.1-pro)" — this means the primary model was temporarily unavailable and the bot gracefully fell back to the next model in the chain. This is expected behavior, not an error.

## 8. Stale Plugin Cleanup

After provider plugin removals, openclaw.json may have stale entries that cause warnings on every command. Remove them:

```bash
openclaw config unset plugins.entries.google-antigravity-auth
```

Then restart the gateway (via launchctl, see §6).

## 9. Re-authenticating openai-codex (OAuth)

When you see `OAuth token refresh failed for openai-codex`, the token has expired. Requires TTY — run manually in terminal:

```bash
openclaw models auth login openai-codex
```

Follow the browser OAuth flow. Gateway picks up the new token automatically (no restart needed).

## 10. Multi-Bot Token Race (refresh_token_reused)

**Symptoms:**
- Multiple VPS bots all fail with `FailoverError: OAuth token refresh failed for openai-codex`
- Error detail: `refresh_token_reused`
- Happens on every container restart

**Root Cause:**
OpenAI uses rotating refresh tokens. If multiple containers share the same openai-codex OAuth account and restart simultaneously, they all try to refresh the same token at once. Only the first succeeds; all others get `refresh_token_reused` and the token is invalidated.

**Fix (immediate):**
Switch VPS bots to `google-antigravity/gemini-3.1-pro` as primary, `openai-codex` as fallback. Antigravity uses a subscription (no rotating tokens), so no race condition on startup. openai-codex is safe as a fallback because bots won't all hit it simultaneously — it only activates when Antigravity is unavailable.

**Recommended final fallback chain (all VPS bots):**
```
primary:   google-antigravity/gemini-3.1-pro
fallback1: openai-codex/gpt-5.3-codex
fallback2: google-antigravity/gemini-3-flash
```

```python
# Run on VPS: python3 fix_models.py
import json
for i in [1, 3, 4, 5, 6, 7, 8, 9]:
    path = f"/root/openclaw/config-bot{i}/openclaw.json"
    with open(path) as f: cfg = json.load(f)
    cfg["agents"]["defaults"]["model"]["primary"] = "google-antigravity/gemini-3-pro-high"
    cfg["agents"]["defaults"]["model"]["fallbacks"] = ["openai-codex/gpt-5.3-codex", "google-antigravity/gemini-3-flash"]
    with open(path, "w") as f: json.dump(cfg, f, indent=2)
```

Then: `cd ~/openclaw && docker compose restart`

**Fix (proper, for openai-codex as primary):**
Each bot needs its own openai-codex OAuth account. Run in each container's TTY:
```bash
docker exec -it openclaw-botX openclaw models auth login openai-codex
```

**Also clean stale plugin warnings** (bot1-6 may have `google-antigravity-auth` stale entry):
```python
for i in [1,3,4,5,6]:
    path = f"/root/openclaw/config-bot{i}/openclaw.json"
    with open(path) as f: cfg = json.load(f)
    cfg.get("plugins",{}).get("entries",{}).pop("google-antigravity-auth", None)
    with open(path, "w") as f: json.dump(cfg, f, indent=2)
```

**Note on bot7/8/9 JSON:** These configs had trailing commas (invalid JSON). Fix before parsing:
```python
import re
content = open(path).read()
fixed = re.sub(r",(\s*[}\]])", r"\1", content)
open(path, "w").write(fixed)
```

## 11. Bot1 Telegram 409 Conflict

**Symptom:** VPS `openclaw-bot1` fails with `409 Conflict` on Telegram polling.

**Cause:** Local openclaw on Mac has the same Telegram bot token as VPS bot1 — two instances polling the same token simultaneously.

**Quick fix (temporary):** Disable Telegram on local openclaw:
```json
// ~/.openclaw/openclaw.json
"channels": { "telegram": { "enabled": false, ... } }
```
Then restart local gateway via launchctl (see §6).

**Proper fix:** Create a separate Telegram bot for local Mac via @BotFather, update `~/.openclaw/openclaw.json` with the new token and re-enable Telegram. Each instance must have its own unique bot token.
- Local Mac bot: `YOUR_BOT_USERNAME` — token `YOUR_TELEGRAM_BOT_TOKEN`

## 6. OpenClaw Docker VPS Deployment (Multi-Bot)

### Structure
On VPS, OpenClaw runs as Docker containers via `~/openclaw/docker-compose.yml`:
- `openclaw-gateway` → `config/`
- `openclaw-bot1` → `config-bot1/`
- `openclaw-bot3` through `openclaw-bot9` → `config-bot3/` … `config-bot9/`
- Each container mounts its own config dir at `/home/node/.openclaw`

### Adding Skills: Per-Bot vs Global

**Per-bot (wrong for shared skills):**
Copy skill into each `config-botX/skills/` — causes drift, no centralized learning.

**Global (correct):**
1. Create shared dir: `mkdir -p ~/openclaw/skills-global/<skill-name>`
2. Add volume to **every** service in `docker-compose.yml`:
   ```yaml
   - ./skills-global:/home/node/.openclaw/skills-global:ro
   ```
3. Add `skills.load.extraDirs` to each `openclaw.json`:
   ```json
   "skills": { "load": { "extraDirs": ["/home/node/.openclaw/skills-global"] } }
   ```
4. `docker compose restart`

### Restarting All Bots
```bash
cd ~/openclaw && docker compose restart
```

### Checking Logs
```bash
docker logs openclaw-gateway --tail 50
docker logs openclaw-bot1 --tail 50
```

## 5. Deep Dive: Why "Reinstalling" Doesn't Fix Data

**Scenario:**
You reinstalled Clawdbot (npm uninstall/install), but the issue (like the hidden agent) persisted.

**Reason:**
Reinstalling only replaces the code binaries (in `/opt/homebrew/lib/...`), but it **does not touch your personal data**.
- **Data Location**: `~/.clawdbot/` (sessions, tokens, configs).
- **The Code**: `/opt/homebrew/lib/node_modules/clawdbot`

**The Fix:**
If you truly need a "clean slate", you must delete the data folder:
```bash
rm -rf ~/.clawdbot
```
*Warning: This deletes all login tokens, message history, and custom settings.*
