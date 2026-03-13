# Domain Mapping System

## Overview

The skill-orchestrator now includes a comprehensive domain mapping system that categorizes all 239 skills by domain and tags, making it easy to discover and query skills by their purpose and capabilities.

## Files

- **skill_domain_map.json** - Complete mapping database with all skills, domains, and tags
- **query_by_domain.py** - CLI tool to query skills by domain or tags
- **browse_domains.py** - Interactive browser for exploring skills by domain

## Quick Start

### List All Domains
```bash
python3 scripts/query_by_domain.py --list-domains
```

### List All Tags
```bash
python3 scripts/query_by_domain.py --list-tags
```

### Query by Domain
```bash
python3 scripts/query_by_domain.py --domain "Content Creation"
python3 scripts/query_by_domain.py --domain "AI & ML"
```

### Query by Tag
```bash
# Find skills with ANY of these tags (OR logic)
python3 scripts/query_by_domain.py --tag python
python3 scripts/query_by_domain.py --tag youtube --tag video

# Find skills with ALL of these tags (AND logic)
python3 scripts/query_by_domain.py --tag python --tag automation --all
```

### Interactive Browser
```bash
python3 scripts/browse_domains.py
```

## Domain Taxonomy

The system organizes skills into 13 primary domains:

1. **AI & ML** - AI models, machine learning, training, and ML tools
2. **Automation & Integration** - Workflow automation, API integration, system integration
3. **Business & Strategy** - Business planning, strategy, operations, consulting
4. **Content Creation** - Writing, research, copywriting, content strategy
5. **Data & Research** - Data analysis, research, scraping, data processing
6. **Development** - Software development, coding, programming tools
7. **E-Commerce** - Product management, marketing, sales, e-commerce operations
8. **Infrastructure & DevOps** - DNS, hosting, cloud, infrastructure management
9. **Media & Design** - Images, video, audio, design, visual content
10. **Personal Development** - Coaching, learning, personal growth
11. **Productivity** - Task management, organization, productivity tools
12. **System & Meta** - Framework, documentation, system management
13. **Web Development** - Frontend, backend, WordPress, web deployment

## Tag System

Skills are tagged with multiple dimensions:

### Technology Tags
- `python`, `nodejs`, `go`, `bash`, `javascript`, `typescript`
- `react`, `nextjs`, `wordpress`, `notion`

### Platform Tags
- `youtube`, `google`, `github`, `twitter`, `reddit`
- `wordpress`, `notion`, `obsidian`

### Use Case Tags
- `research`, `generation`, `optimization`, `automation`
- `analysis`, `testing`, `deployment`, `monitoring`

### Content Type Tags
- `text`, `image`, `video`, `audio`, `data`

## Data Structure

### skill_domain_map.json

```json
{
  "total_skills": 239,
  "domains": {
    "Content Creation": ["skill1", "skill2", ...],
    "AI & ML": ["skill3", "skill4", ...]
  },
  "domain_counts": {
    "Content Creation": 45,
    "AI & ML": 38
  },
  "tags": {
    "python": ["skill1", "skill3", ...],
    "youtube": ["skill2", "skill5", ...]
  },
  "tag_counts": {
    "python": 67,
    "youtube": 23
  },
  "skills": {
    "skill-name": {
      "name": "skill-name",
      "description": "...",
      "primary_domain": "Content Creation",
      "tags": ["python", "youtube", "automation"],
      "dependencies": ["other-skill"],
      "output_formats": ["json", "markdown"]
    }
  }
}
```

## Query Examples

### Find All Python Skills
```bash
python3 scripts/query_by_domain.py --tag python
```

### Find YouTube Content Creation Skills
```bash
python3 scripts/query_by_domain.py --tag youtube --tag content
```

### Find Skills That Do Both Research AND Generation
```bash
python3 scripts/query_by_domain.py --tag research --tag generation --all
```

### Browse All AI & ML Skills
```bash
python3 scripts/query_by_domain.py --domain "AI & ML"
```

## Integration with Other Tools

### With skill-lookup
```bash
# Find skills by domain first
python3 scripts/query_by_domain.py --domain "Content Creation"

# Then use skill-lookup for detailed info
python3 ~/.claude/skills/skill-lookup/scripts/skill_lookup.py <skill-name>
```

### With skill-creator
When creating new skills, reference the domain taxonomy to assign appropriate:
- Primary domain
- Tags (technology, platform, use case)
- Output formats

### With skill-improver
Use domain mapping to find similar skills and ensure consistency within domains.

## Maintenance

### Updating the Mapping

When new skills are added or existing skills are modified:

```bash
# Regenerate domain mapping
cd ~/.claude/skills/skill-orchestrator
python3 scripts/regenerate_domain_map.py --verbose
```

The script will:
1. Scan all skills in both Gemini and Claude directories
2. Extract metadata from SKILL.md files
3. Classify skills into domains using pattern matching
4. Extract tags from skill descriptions
5. Regenerate the skill_domain_map.json database

**Automatic classification**: The script uses regex patterns to classify skills:
- Checks skill descriptions against domain patterns
- Extracts technology, platform, and use case tags
- Identifies dependencies and output formats
- Prefers Gemini as source of truth when merging

### Adding New Domains

Edit the domain classification logic in the metadata extraction scripts to recognize new domain patterns.

### Adding New Tags

Tags are automatically extracted from skill descriptions and metadata. To add custom tags, update the skill's SKILL.md frontmatter.

## Statistics

- **Total Skills**: 239
- **Domains**: 13
- **Tags**: 29
- **Average Tags per Skill**: 3.2
- **Most Common Domain**: AI & ML (38 skills)
- **Most Common Tag**: python (67 skills)

## Use Cases

### 1. Skill Discovery
"I need a skill that works with YouTube videos"
```bash
python3 scripts/query_by_domain.py --tag youtube --tag video
```

### 2. Technology Stack Planning
"What skills use Python and automation?"
```bash
python3 scripts/query_by_domain.py --tag python --tag automation --all
```

### 3. Domain Exploration
"What content creation skills are available?"
```bash
python3 scripts/browse_domains.py
# Select "Content Creation" from menu
```

### 4. Workflow Planning
"Find skills for a research → write → publish workflow"
```bash
python3 scripts/query_by_domain.py --tag research
python3 scripts/query_by_domain.py --tag writing
python3 scripts/query_by_domain.py --tag publishing
```

## Future Enhancements

- [ ] Skill relationship graph visualization
- [ ] Workflow template generation based on domain
- [ ] Automatic skill recommendation based on task description
- [ ] Domain-specific best practices documentation
- [ ] Cross-domain skill compatibility matrix
