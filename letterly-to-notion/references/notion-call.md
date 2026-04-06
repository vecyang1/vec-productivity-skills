# notion-create-pages Call Reference

Exact MCP tool call format for pushing a Letterly note to the Notion Content[UB3_250711] database.

## Tool

`mcp__b465a3b1-186c-4ab2-aaeb-fd8e42672261__notion-create-pages`

## Parameters

```
parent:
  type: "data_source_id"
  data_source_id: "22ce1b43-2393-81f8-8fc6-000b9bba5c67"

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
    "data_source_id": "22ce1b43-2393-81f8-8fc6-000b9bba5c67"
  },
  "pages": [
    {
      "properties": {
        "Name": "AI时代下的个人追求",
        "Status": "Idea",
        "Media Type": "[\"Audio\"]",
        "Source": "Letterly #1894788",
        "Tags": "[\"China\"]",
        "date:Writtern date:start": "2026-07-17"
      },
      "content": "今天我想聊一下在AI时代，我们作为个人应该追求什么。很多人觉得AI会取代一切，但我认为恰恰相反..."
    }
  ]
}
```

## Response Format

The tool returns a page URL on success. Extract it for the index:

```
notion_url: "https://www.notion.so/AI-1894788abc123..."
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

Format: `Letterly #<note_id>` (e.g., `Letterly #1894788`). Before creating, you can search for existing pages with the same Source value to avoid duplicates:

```
notion-search(query="Letterly #1894788", data_source_url="collection://22ce1b43-2393-81f8-8fc6-000b9bba5c67")
```

### One page per call

Push one note at a time, not batched. Write the index to disk after each successful create. This prevents data loss if a subsequent push fails.
