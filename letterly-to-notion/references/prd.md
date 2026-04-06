# PRD: Letterly-to-Notion Content Pipeline

## 1. Introduction

A Claude Code skill that bridges Letterly (voice transcription app) and Notion's Content[UB3_250711] database. It pulls voice notes from Letterly, presents them for selective approval, pushes approved ones to Notion as content ideas, and maintains a persistent index to prevent duplicates and track processing history.

**This is a skill (SKILL.md) — not a deployed app.** It guides future Claude Code agents through the pipeline workflow.

## 2. Goals

- Pull unprocessed Letterly notes and present them for user review
- Push user-approved notes to Notion Content[UB3_250711] as "Idea" status entries
- Maintain a JSON index tracking: note ID, title, processed date, Notion page URL
- Support periodic sync (pull new, skip already-processed)
- Batch operations: approve/reject multiple notes at once
- Zero data loss: never push without explicit user approval

## 3. User Stories

### US-001: Pull and Review Notes
**Description:** As a content creator, I want to see my recent Letterly notes so I can decide which ones become content ideas.

**Acceptance Criteria:**
- [ ] List Letterly notes with ID, title, date, and preview (first 80 chars)
- [ ] Mark notes already in index as "processed" with date
- [ ] New (unprocessed) notes clearly identified
- [ ] Support pagination (20 notes per page)

### US-002: Selective Push to Notion
**Description:** As a content creator, I want to choose which notes to push to Notion so only quality content enters my pipeline.

**Acceptance Criteria:**
- [ ] Present each unprocessed note for approval (show full content)
- [ ] User can approve, skip, or mark as "never push"
- [ ] Approved notes create a Notion page with correct field mapping
- [ ] Index updated immediately after successful push

### US-003: Track Processing History
**Description:** As a content creator, I want to know which notes have been processed so I never duplicate work.

**Acceptance Criteria:**
- [ ] JSON index persists across sessions
- [ ] Each entry records: letterly_id, title, processed_date, notion_url, status (pushed/skipped/rejected)
- [ ] Index queryable: "show me what I processed last week"

### US-004: Periodic Sync
**Description:** As a content creator, I want to periodically sync to catch new notes without re-reviewing old ones.

**Acceptance Criteria:**
- [ ] Pull all notes, diff against index, show only new/unprocessed
- [ ] Support "sync since last run" based on index timestamps
- [ ] Handle Letterly pagination (6 pages, 113+ notes)

## 4. Functional Requirements

- FR-1: Pull notes via `list_notes` MCP tool with pagination (page_size=20)
- FR-2: Pull individual note details via `get_note` for full content + improvements
- FR-3: Compare pulled notes against local JSON index by `note_id`
- FR-4: Present unprocessed notes to user with title, date, preview
- FR-5: On approval, create Notion page via `notion-create-pages` with mapping:
  - `Name` ← Letterly note title
  - `Status` ← "Idea"
  - `Media Type` ← `["Audio"]`
  - `Source` ← `"Letterly #<note_id>"`
  - `Tags` ← auto-detect language from content (Chinese→"China", Vietnamese→"Viet", Spanish→"Thai"/"Nomad", English→no tag or "Culture")
  - Page body ← full transcript text
  - `date:Writtern date:start` ← note created timestamp (converted to ISO-8601)
- FR-6: Update index after each push with `notion_url`, `processed_date`, `status`
- FR-7: Support batch mode: list all unprocessed, user selects multiple by ID
- FR-8: `search_notes` for keyword-based filtering before review

## 5. Non-Goals

- No automatic push without user approval
- No Letterly rewriting/cleanup (user chose raw push)
- No editing of existing Notion pages (create-only)
- No syncing from Notion back to Letterly
- No scheduled cron automation (manual trigger only)

## 6. Stack & Dependencies

| Dependency | Type | Purpose |
|---|---|---|
| Letterly MCP | MCP server | Read notes, search, get details |
| Notion MCP (`claude_ai_Notion`) | MCP server | Create pages in Content[UB3_250711] |
| JSON index file | Local file | Track processing state |
| notion-mcp-connector skill | Reference | Notion patterns and conventions |

No new packages needed. Pure MCP tool orchestration.

## 7. Safety

### 7.1 Zero-Regression
- Read-only on Letterly (no deletes, no updates to notes)
- Create-only on Notion (no updates to existing pages)
- Index file: append-only updates (never delete entries)

### 7.2 Data Safety
- Always confirm with user before pushing any note
- Show full content preview before approval
- Log every push with timestamp and Notion URL
- Index serves as audit trail

### 7.3 Error Handling
| Failure | Response | Recovery |
|---|---|---|
| Letterly MCP unavailable | Show error, suggest reconnecting | Retry on next run |
| Notion MCP unavailable | Show error, don't mark as processed | Notes remain unprocessed in index |
| Notion create fails | Log error, don't update index | Retry on next run |
| Index file corrupted | Rebuild from Notion search | Search Notion for "Letterly #" sources |

## 8. Index System

### 8.1 File Location
```
~/.claude/skills/letterly-to-notion/index.json
```

### 8.2 Schema
```json
{
  "version": 1,
  "last_sync": "2026-04-04T12:00:00+08:00",
  "last_letterly_page": 1,
  "notes": {
    "2010883": {
      "title": "皮肤皱纹也少诶",
      "letterly_created": "2026-08-02T10:30:31+08:00",
      "status": "pushed",
      "processed_date": "2026-04-04T12:05:00+08:00",
      "notion_url": "https://www.notion.so/...",
      "detected_language": "zh"
    },
    "1995209": {
      "title": "Noticias de salud y cocina",
      "letterly_created": "2026-07-30T14:19:17+08:00",
      "status": "skipped",
      "processed_date": "2026-04-04T12:06:00+08:00",
      "notion_url": null,
      "detected_language": "es"
    }
  }
}
```

### 8.3 Status Values
- `pushed` — Successfully created in Notion
- `skipped` — User chose to skip (can revisit later)
- `rejected` — User explicitly said "never push"
- `pending` — Pulled but not yet reviewed

## 9. Field Mapping Reference

### Notion Content[UB3_250711] Target Fields

| Notion Property | Type | Source | Value |
|---|---|---|---|
| `Name` | title | Letterly note title | Direct copy |
| `Status` | status | Hardcoded | `"Idea"` |
| `Media Type` | multi_select | Hardcoded | `["Audio"]` |
| `Source` | text | Letterly note ID | `"Letterly #<id>"` |
| `Tags` | multi_select | Language detection | See language map |
| `date:Writtern date:start` | date | Letterly created timestamp | ISO-8601 date |
| Page body | content | Letterly transcript | Full raw text |

### Language → Tag Mapping
| Detected Language | Notion Tag |
|---|---|
| Chinese (zh) | `China` |
| Vietnamese (vi) | `Viet` |
| Japanese (ja) | `Japan` |
| Thai (th) | `Thai` |
| Spanish (es) | (no auto-tag, ask user) |
| English (en) | (no auto-tag, ask user) |
| Mixed/Unknown | (ask user) |

### Data Source ID
```
collection://22ce1b43-2393-81f8-8fc6-000b9bba5c67
```

### Database URL
```
https://www.notion.so/22ce1b43239381c1993ecf632dad6d2d
```

## 10. Success Metrics

- Notes processed without duplication (index dedup works)
- User can review and push 10+ notes in a single session
- Zero accidental pushes (always asks permission)
- Index survives across sessions and agents

## 11. Open Questions

None — all decisions resolved via user answers:
- Status: Idea
- Rewrite: No (push raw)
- Content: Page body only
- Media Type: Audio
- Tags: Auto-detect language
