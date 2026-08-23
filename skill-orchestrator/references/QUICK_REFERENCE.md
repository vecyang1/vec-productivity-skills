# Domain Mapping Quick Reference

## 📊 Stats
- **Total Skills**: 239
- **Domains**: 13
- **Tags**: 29
- **Location**: `~/.claude/skills/skill-orchestrator/references/`

## 🚀 Quick Commands

```bash
# List all domains
python3 ~/.claude/skills/skill-orchestrator/scripts/query_by_domain.py --list-domains

# List all tags
python3 ~/.claude/skills/skill-orchestrator/scripts/query_by_domain.py --list-tags

# Find skills by domain
python3 ~/.claude/skills/skill-orchestrator/scripts/query_by_domain.py --domain "AI & ML"

# Find skills by tag (OR logic)
python3 ~/.claude/skills/skill-orchestrator/scripts/query_by_domain.py --tag python

# Find skills with ALL tags (AND logic)
python3 ~/.claude/skills/skill-orchestrator/scripts/query_by_domain.py --tag python --tag automation --all

# Interactive browser
python3 ~/.claude/skills/skill-orchestrator/scripts/browse_domains.py
```

## 📁 13 Domains

1. **AI & ML** (76) - AI models, ML, training
2. **Content Creation** (35) - Writing, research
3. **Image & Design** (27) - Images, design
4. **Development & Code** (18) - Software dev
5. **Automation & Integration** (12) - Workflows, APIs
6. **Business & Productivity** (11) - Planning, productivity
7. **Data & Analytics** (10) - Data analysis
8. **Research & Knowledge** (8) - Research tools
9. **Video & Media** (6) - Video, audio
10. **E-commerce** (6) - Product, sales
11. **Social Media** (3) - Social platforms
12. **Education** (1) - Educational
13. **(Uncategorized)** (26) - Needs review

## 🏷️ Top Tags

- **python** (52) - Python-based skills
- **generation** (31) - Content generation
- **image** (28) - Image processing
- **automation** (24) - Automation tools
- **text** (23) - Text processing
- **optimization** (21) - Optimization tools
- **data** (20) - Data handling
- **video** (18) - Video processing
- **nodejs** (15) - Node.js based
- **youtube** (14) - YouTube integration

## 📚 Documentation

- **DOMAIN_GUIDE.md** - Complete guide with examples
- **DOMAIN_MAPPING_COMPLETE.md** - Project summary
- **skill_domain_map.json** - Full database (165KB)

## 💡 Common Use Cases

### Find YouTube Skills
```bash
python3 scripts/query_by_domain.py --tag youtube
```

### Find Python Automation Skills
```bash
python3 scripts/query_by_domain.py --tag python --tag automation --all
```

### Browse Content Creation Skills
```bash
python3 scripts/query_by_domain.py --domain "Content Creation"
```

### Explore Interactively
```bash
python3 scripts/browse_domains.py
```

## 🔗 Integration

Works with:
- **skill-lookup** - Get detailed skill info
- **skill-creator** - Reference when creating skills
- **skill-improver** - Find similar skills
- **skill-orchestrator** - All existing features

## 📝 Files

```
~/.claude/skills/skill-orchestrator/
├── references/
│   ├── skill_domain_map.json          # Main database
│   ├── DOMAIN_GUIDE.md                # Full documentation
│   ├── DOMAIN_MAPPING_COMPLETE.md     # Project summary
│   └── QUICK_REFERENCE.md             # This file
├── scripts/
│   ├── query_by_domain.py             # Query tool
│   └── browse_domains.py              # Interactive browser
└── SKILL.md                           # Updated main doc
```
