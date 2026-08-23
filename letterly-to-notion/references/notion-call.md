# notion-create-pages Call Reference

Exact MCP tool call format for pushing a Letterly note to your Notion Content database.

## Tool

`mcp__YOUR_NOTION_MCP_UUID__notion-create-pages`

> Replace `YOUR_NOTION_MCP_UUID` with the UUID from your own Notion MCP server connection.

## Parameters

```
parent:
  type: "data_source_id"
  data_source_id: "YOUR_NOTION_DB_ID"

pages: (array of one page object)
  properties:
    Name:                       "<note title>"
    Status:                     "Idea"
    Media Type:                 "[\"Audio\"]"
    Source:                     "Letterly #<note_id>"
    Tags:                       "[\"China\"]"
    date:Writtern date:start:   "2026-04-02"

  content: "<full transcript text>"
```

## Concrete Example

```json
{
  "parent": {
    "type": "data_source_id",
    "data_source_id": "YOUR_NOTION_DB_ID"
  },
  "pages": [
    {
      "properties": {
        "Name": "My voice note title",
        "Status": "Idea",
        "Media Type": "[\"Audio\"]",
        "Source": "Letterly #1234567",
        "Tags": "[\"China\"]",
        "date:Writtern date:start": "2026-04-02"
      },
      "content": "Full transcript text goes here..."
    }
  ]
}
```

## Response Format

The tool returns a page URL on success. Extract it for the index:

```
notion_url: "https://www.notion.so/My-note-title-abc123..."
```

Use this URL in the index entry under `notion_url`.

## Gotchas

### Media Type must be a JSON array string

```
WRONG:   "Media Type": "Audio"
WRONG:   "Media Type": ["Audio"]
CORRECT: "Media Type": "[\"Audio\"]"
```

The property is a multi-select. The value must be a JSON-encoded array string, not a bare string or a native array.

### Tags must be a JSON array string

```
WRONG:   "Tags": "China"
WRONG:   "Tags": ["China", "Viet"]
CORRECT: "Tags": "[\"China\"]"
CORRECT: "Tags": "[\"China\", \"Viet\"]"
```

Same rule as Media Type. Multi-select properties require JSON array strings.

### Date format must be date-only (no datetime)

```
WRONG:   "date:Writtern date:start": "2026-04-02T14:30:00+08:00"
WRONG:   "date:Writtern date:start": "2026-04-02T00:00:00Z"
CORRECT: "date:Writtern date:start": "2026-04-02"
```

Use ISO-8601 date only (`YYYY-MM-DD`). Adding a time component can cause unexpected behavior.

### Status must match exact option name

```
WRONG:   "Status": "idea"
WRONG:   "Status": "IDEA"
WRONG:   "Status": "Draft"
CORRECT: "Status": "Idea"
```

Case-sensitive. Must match one of the select options defined in the database schema.

### The date property has a typo in the schema

The property is literally named `Writtern date` (with double-t). Do not "fix" it to `Written date`. The expanded form is:

```
date:Writtern date:start
```

### Source field is for dedup tracking

Format: `Letterly #<note_id>` (e.g., `Letterly #1234567`). Before creating, you can search for existing pages with the same Source value to avoid duplicates:

```
notion-search(query="Letterly #1234567", data_source_url="collection://YOUR_NOTION_DB_ID")
```

### One page per call

Push one note at a time, not batched. Write the index to disk after each successful create. This prevents data loss if a subsequent push fails.
