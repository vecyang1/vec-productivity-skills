# Domain Mapping Acceleration Guide for Future Agents

## Quick Start

When you need to work with skill domain mapping or regenerate it:

```bash
# Regenerate entire domain mapping database
cd ~/.claude/skills/skill-orchestrator
python3 scripts/regenerate_domain_map.py --verbose

# Query skills by domain
python3 scripts/query_by_domain.py --domain "AI & ML"

# Query skills by tags
python3 scripts/query_by_domain.py --tag python --tag automation --all

# Interactive browser
python3 scripts/browse_domains.py
```

## What This System Does

**Automatically categorizes all skills** in both Gemini and Claude directories into:
- **13 domains** (AI & ML, Content Creation, Web Development, etc.)
- **29 tags** (python, youtube, automation, generation, etc.)
- **Dependencies** (which skills reference other skills)
- **Output formats** (json, markdown, image, video, etc.)

## How It Works

### 1. Scanning
- Scans `~/.gemini/antigravity/skills/` and `~/.claude/skills/`
- Reads each `SKILL.md` file
- Extracts description from frontmatter or first paragraph

### 2. Classification
Uses regex pattern matching on skill content:

**Domain patterns** (13 domains):
- AI & ML: `\bai\b`, `\bml\b`, `machine learning`, `model`, `gemini`, `claude`
- Content Creation: `content`, `writing`, `copywriting`, `research`, `seo`
- Image & Design: `image`, `photo`, `design`, `visual`, `banner`, `logo`
- Video & Media: `video`, `audio`, `youtube`, `transcribe`, `editing`
- Web Development: `wordpress`, `wp-`, `react`, `nextjs`, `frontend`
- And 8 more...

**Tag patterns** (29 tags):
- Technology: `python`, `nodejs`, `go`, `bash`, `react`, `wordpress`
- Platform: `youtube`, `google`, `github`, `twitter`, `notion`
- Use Case: `research`, `generation`, `optimization`, `automation`
- Content Type: `text`, `image`, `video`, `audio`, `data`

### 3. Output
Generates `skill_domain_map.json` with:
```json
{
  "total_skills": 239,
  "domains": {"AI & ML": ["skill1", "skill2"]},
  "domain_counts": {"AI & ML": 76},
  "tags": {"python": ["skill1", "skill3"]},
  "tag_counts": {"python": 52},
  "skills": {
    "skill-name": {
      "name": "skill-name",
      "description": "...",
      "primary_domain": "AI & ML",
      "tags": ["python", "automation"],
      "dependencies": ["other-skill"],
      "output_formats": ["json", "markdown"]
    }
  }
}
```

## When to Regenerate

Run `regenerate_domain_map.py` when:
- ✅ New skills added to either directory
- ✅ Skill descriptions updated in SKILL.md
- ✅ Skills renamed or moved
- ✅ Need fresh classification after bulk changes

**Frequency**: After any skill changes, or weekly for maintenance

## Performance

- **Speed**: ~2-3 seconds for 239 skills
- **Memory**: Minimal (processes one skill at a time)
- **Output**: ~165KB JSON file

## Integration Points

### With skill-creator
After creating a new skill, regenerate to include it in domain mapping.

### With skill-improver
Query similar skills in same domain before improving.

### With skill-lookup
Use domain mapping to find skills, then skill-lookup for details.

## Customization

### Adding New Domains
Edit `DOMAIN_PATTERNS` in `regenerate_domain_map.py`:
```python
DOMAIN_PATTERNS = {
    "Your New Domain": [
        r"pattern1", r"pattern2", r"pattern3"
    ]
}
```

### Adding New Tags
Edit `TAG_PATTERNS` in `regenerate_domain_map.py`:
```python
TAG_PATTERNS = {
    "your-tag": r"\byour-pattern\b"
}
```

## Troubleshooting

### Skills Not Classified
- Check if SKILL.md exists
- Verify description is in frontmatter or first paragraph
- Add more specific patterns to DOMAIN_PATTERNS

### Wrong Domain Assignment
- Skill matched multiple patterns - highest match count wins
- Add more specific patterns for correct domain
- Or manually override in skill's SKILL.md

### Missing Tags
- Tag patterns are case-insensitive
- Check if pattern matches skill content
- Add new patterns to TAG_PATTERNS

## Files Structure

```
~/.claude/skills/skill-orchestrator/
├── scripts/
│   ├── regenerate_domain_map.py       # Main regeneration script
│   ├── query_by_domain.py             # Query tool
│   └── browse_domains.py              # Interactive browser
├── references/
│   ├── skill_domain_map.json          # Generated database
│   ├── DOMAIN_GUIDE.md                # User documentation
│   └── DOMAIN_MAPPING_ACCELERATION.md # This file
└── SKILL.md                           # Main skill documentation
```

## Example Workflow

### Scenario: User adds 5 new skills

```bash
# 1. User creates skills in Gemini directory
# (skills automatically sync to Claude via skill-symlink-sync)

# 2. Regenerate domain mapping
cd ~/.claude/skills/skill-orchestrator
python3 scripts/regenerate_domain_map.py --verbose

# 3. Verify new skills are classified
python3 scripts/query_by_domain.py --list-domains

# 4. Check specific domain
python3 scripts/query_by_domain.py --domain "AI & ML"

# 5. Browse interactively
python3 scripts/browse_domains.py
```

### Scenario: User wants Python automation skills

```bash
# Query with AND logic (must have both tags)
python3 scripts/query_by_domain.py --tag python --tag automation --all

# Or browse by domain first
python3 scripts/browse_domains.py
# Select "Automation & Integration"
# Look for Python-tagged skills
```

## Key Insights for Agents

1. **Gemini is source of truth** - When merging, Gemini skills override Claude
2. **Pattern-based classification** - No ML, just regex patterns
3. **Automatic extraction** - No manual tagging needed
4. **Fast regeneration** - Can run frequently without performance impact
5. **Self-contained** - No external dependencies beyond Python stdlib

## Memory Update

This capability has been added to global memory at:
`~/.claude/projects/-Users-vecsatfoxmailcom/memory/MEMORY.md`

Under "Skill-Specific Rules" → "skill-orchestrator"

## Success Metrics

- ✅ 239 skills categorized
- ✅ 13 domains defined
- ✅ 29 tags extracted
- ✅ ~2 second regeneration time
- ✅ 165KB database size
- ✅ Zero manual intervention needed

## Future Enhancements

Potential improvements for future agents:
- [ ] ML-based classification (more accurate than regex)
- [ ] Skill similarity scoring
- [ ] Automatic workflow generation from domain combinations
- [ ] Domain-specific best practices extraction
- [ ] Cross-domain compatibility matrix
- [ ] Skill recommendation engine based on task description
