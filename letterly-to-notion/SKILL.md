---
name: letterly-to-notion
description: Pull voice notes from Letterly, selectively push to a Notion Content database as Ideas. Tracks processed notes via index.json. Trigger on "sync letterly", "push notes", "letterly", "process voice notes".
---

# Letterly → Notion Pipeline

## IDs
- **Notion data_source_id**: `YOUR_NOTION_DB_ID` — replace with your own database ID
- **Index**: `~/.claude/skills/letterly-to-notion/index.json`
- **PRD**: `references/prd.md`

## Prerequisites Check

Before starting, verify both MCPs respond:
1. `list_notes(page=1, page_size=1)` — if fails → "Connect Letterly MCP first"
2. `get_user_info()` — confirms Letterly auth
3. Notion: `notion-fetch` on `YOUR_NOTION_DB_ID` — if fails → "Share DB with Notion integration"

## Workflow

### Step 1: Load Index
Read `~/.claude/skills/letterly-to-notion/index.json`. If missing, init:
```json
{"version":1,"last_sync":null,"notes":{}}
```

### Step 2: Pull & Diff
```
list_notes(page=1, page_size=20)
```
For each note: check `index.notes[note_id]`:
- Not in index → **NEW** — also write to index as `status: "pending"` with `char_count` and `preview` (first 100 chars from list_notes snippet)
- `status: "pending"` or `"skipped"` → **show again** for review
- `status: "pushed"` or `"rejected"` → skip silently

Paginate until all pages fetched or user says stop. Letterly has ~6+ pages (113+ notes).

**Important**: Writing pending notes to index during pull ensures the `ltl` dashboard has data for ALL notes, not just actioned ones.

### Step 3: Present for Approval
Show **only NEW + SKIPPED** in a table. Include **word count** and **quality tier** to help user filter:

```markdown
| # | ID | Title | Date | Chars | Tier | Lang | Status |
|---|---------|-------------------------------|------------|-------|---------|------|---------|
| 1 | 1234567 | My voice note about topic A   | 2026-04-04 | 1850 | content | zh | NEW |
| 2 | 1234568 | Another substantial note      | 2026-04-04 | 2100 | content | zh | NEW |
| 3 | 1234569 | Short idea fragment           | 2026-04-04 | 30   | spark   | zh | NEW |
| 4 | 1234570 | Trivial comment               | 2026-04-04 | 12   | snippet | zh | NEW |
| 5 | 1234571 | Casual reminder to self       | 2026-04-03 | 45   | snippet | zh | NEW |
```

**Quality Tiers** (based on character count of transcript):
- `content` (500+ chars) — substantial, worth pushing
- `note` (200-499) — moderate, likely useful
- `spark` (50-199) — short idea fragment
- `snippet` (<50) — likely trivial/casual chat

Then ask:
> Which notes to push? Numbers (1,2,5), "all", or "none". You can also "reject 4,5" to permanently exclude snippets.

**NEVER auto-push. NEVER skip this question.**

### Step 4: Push Each Approved Note

For each approved note, execute this exact sequence:

**4a. Fetch full content:**
```
get_note(note_id=<id>)
```

**4b. Show content to user** — display title + first 200 chars of transcript. Confirm proceed.

**4c. Detect language** from transcript content (see Language Detection below).

**4d. Convert timestamp** — Letterly `created` is Unix milliseconds. Use python3 or equivalent:
```python
from datetime import datetime, timezone
dt = datetime.fromtimestamp(1775301031000/1000, tz=timezone.utc)
# → "2026-04-04" (date only, YYYY-MM-DD format)
```
**WARNING**: Do NOT manually calculate dates — always use a proper datetime library.

**4e. Create Notion page** — exact call format in `references/notion-call.md`. Key params:
```
parent: { data_source_id: "YOUR_NOTION_DB_ID" }
properties:
  Name: "<note title>"
  Status: "Idea"
  Media Type: "[\"Audio\"]"
  Source: "Letterly #<note_id>"
  Tags: "<detected tags JSON array>"
  date:Writtern date:start: "<YYYY-MM-DD>"
content: (see Page Body Format below)
```

**Page Body Format** — prepend a source callout for searchability:
```markdown
> **Source:** Letterly voice note #<note_id> | Recorded: <YYYY-MM-DD>
> **Chars:** <count> | **Tier:** <tier> | **Language:** <lang>

---

<full raw transcript text>
```
This ensures Notion's search finds these pages when searching "Letterly" or note IDs.

**4f. Update index** — immediately after successful Notion create:
```json
"<note_id>": {
  "title": "<title>",
  "letterly_created": "<ISO>",
  "status": "pushed",
  "processed_date": "<now ISO>",
  "notion_url": "<page URL from response>",
  "detected_language": "<lang>"
}
```

**4g. Write index to disk** — after EACH note, not batched. Prevents data loss if next push fails.

### Step 4h: Process Dashboard Queue
Before Step 5, check `action_queue.json` for notes queued via the web dashboard:
```
Read: ~/.claude/skills/letterly-to-notion/action_queue.json
```
For each `action: "push"` entry: execute Steps 4a-4g for that note_id. After processing, clear the queue. Notes queued via dashboard may have `tags_override` in index — use those tags instead of auto-detect.

### Step 5: Finalize
Update `last_sync` to current ISO timestamp. Write index. Show summary:
```
Pushed: 3 notes
Skipped: 1 note
Rejected: 0 notes
Queued (processed): 2 notes
Remaining unprocessed: 12 notes
```

## Language Detection

Scan transcript text for dominant script:

| Signal | Language | Notion Tag |
|--------|----------|------------|
| CJK Unified chars (>50% of text) | zh | `"China"` |
| Vietnamese diacritics: ơ ư ắ ề ổ ử | vi | `"Viet"` |
| Hiragana/Katakana | ja | `"Japan"` |
| Thai script range (U+0E00-0E7F) | th | `"Thai"` |
| ¿ ñ está es/son conjugations | es | **ASK user** |
| Latin-only, no markers | en | **ASK user** |
| Multiple scripts detected | mixed | **ASK user** |

For es/en/mixed: show content sample and ask "What Tags for this note?"

## Index Schema (v2)

```json
{
  "version": 2,
  "last_sync": "2026-04-04T12:00:00+08:00",
  "notes": {
    "<note_id>": {
      "title": "string",
      "letterly_created": "ISO-8601",
      "status": "pushed | skipped | rejected | pending",
      "processed_date": "ISO-8601 | null",
      "notion_url": "string | null",
      "detected_language": "zh|en|vi|ja|th|es|mixed",
      "char_count": "int | null",
      "preview": "first ~100 chars | null"
    }
  }
}
```

**v2 additions**: `char_count`, `preview`, and `pending` status. During Step 2, write ALL pulled notes to index (pending ones included) so the dashboard has complete data.

## Safety Rules

1. **NEVER push without user approval** — present content, ask, wait for yes
2. **NEVER modify existing Notion pages** — create-only operations
3. **NEVER delete or update Letterly notes** — read-only access
4. **ALWAYS write index after each push** — not batched, prevents data loss
5. **If either MCP disconnected** → stop workflow, tell user, don't mark anything as processed

## Error Recovery

| Error | Action | DO NOT |
|-------|--------|--------|
| Notion create fails (403/500) | Log error, keep note as unprocessed | Mark as pushed |
| Letterly MCP timeout | Retry once, then stop batch | Continue with partial data |
| Index file corrupted/missing | Rebuild from Notion (see below) | Start fresh empty index |
| Duplicate detected (Source already exists) | Skip, mark as pushed in index | Create duplicate page |

**Rebuild index from Notion:**
```
notion-search(query="Letterly #", data_source_url="collection://YOUR_NOTION_DB_ID")
```
Parse each result's `Source` field → extract note ID → add to index as `status: "pushed"`.

## Backup & Recovery

**Auto-backup**: Server creates backups on startup + every hour in `backups/` (max 10 kept).

**Manual backup**: `POST /api/backup` or from Claude: read and copy `index.json`.

**Restore**: `POST /api/restore` with optional `{"backup_name": "index_20260404_200000_startup.json"}`. Defaults to latest. Always backs up current state before restoring.

**List backups**: `GET /api/backups` — returns all backup files with note counts.

**Full rebuild from scratch** (if everything is lost):
1. Pull all notes from Letterly: `list_notes` across all pages → write to index as `pending`
2. Rebuild pushed notes from Notion: `notion-search(query="Letterly #")` → mark as `pushed`
3. Re-run `sync letterly` to reconcile

**Critical files** (never delete):
- `index.json` — all state lives here (113+ notes, statuses, Notion URLs)
- `config.json` — server configuration
- `backups/` — automatic safety net

## Utility Commands

| User says | Action |
|-----------|--------|
| "sync letterly" | Full workflow Steps 1-5 |
| "letterly stats" | Read index, show pushed/skipped/rejected counts |
| "search letterly <keyword>" | `search_notes(query)` → approval flow |
| "letterly rebuild" | Rebuild index from Notion |
| `ltl` (shell alias) | Generate + open HTML dashboard in browser |
| "letterly dashboard" | Same as `ltl` — run `scripts/dashboard.py` |
| "show skipped" | Filter index for skipped, re-present for approval |
| "reject <id>" | Set index status to "rejected" |

## Dashboard (`ltl`)

**Live HTTP server** on port 5588 (configurable via `config.json` or `LTL_PORT` env var).

```bash
# Shell alias (in ~/.zshrc)
alias ltl='python3 ~/.claude/skills/letterly-to-notion/scripts/dashboard.py &; sleep 1 && open http://localhost:5588'
```

**Features:**
- Auto-refresh every 10s (polls `/api/notes`)
- Multi-select checkboxes + floating bulk action bar (Push/Skip/Reject/Undo)
- Per-row actions: Push, Skip, Reject, Undo
- **Click title** → detail modal: view full transcript, edit title/tags, Save & Push
- **Notion** link opens pushed page in Notion
- Note: Letterly has no web URLs for individual notes (mobile app only), and no audio file export via MCP (text transcripts only)
- Filter by status, tier, language + full-text search
- Sortable columns (click header)
- Clickable stat cards filter by status
- Queue banner: shows when notes queued for push
- Letterly-styled UI (Onest font, #8B7FFF accent, #FEF8FB background)

**API Endpoints:**
```
GET  /              Dashboard HTML
GET  /api/notes     All notes from index.json
GET  /api/stats     Summary statistics
GET  /api/config    Server config
GET  /api/queue     Pending action queue
GET  /api/health    Health check
POST /api/action    Single action {action, note_id}
POST /api/bulk      Batch action {action, note_ids[]}
POST /api/queue/clear  Clear action queue
```

**Action Queue:** When user clicks Push in the dashboard, the note is added to `action_queue.json` with `queued_push` status. Next time `sync letterly` runs in Claude, it reads the queue and processes pushes via Notion MCP.

**Config** (`config.json`):
```json
{"port":5588,"refresh_interval_seconds":10,"default_sort":"date","default_sort_dir":"desc"}
```

## References (load on demand)

- `references/prd.md` — Full PRD for this skill
- `references/notion-call.md` — exact `notion-create-pages` call with real example
- `references/prompts.md` — Letterly rewrite prompt IDs (if user wants cleanup)
- `notion-mcp-connector` skill — Notion patterns, error handling, troubleshooting
