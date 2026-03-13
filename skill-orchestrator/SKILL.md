---
name: skill-orchestrator
description: Manage skill relationships, workflows, domain mapping, and design coherence. Use when you need to discover skills by domain/tags, find which skills work together, track workflow chains, ensure consistent design language across related skills, or audit skill dependencies. Handles skill relationship mapping, domain categorization, workflow orchestration, design language enforcement, and cross-skill coordination.
---

# Skill Orchestrator

## Overview

Manages skill relationships, domain mapping, workflow chains, and design coherence across the skill ecosystem. Provides comprehensive domain categorization and tagging system for all 239 skills, tracks which skills work together, documents multi-skill workflows, and ensures consistent design language.

## Image Generation Skills - Prompt Design Guidance

**For all image gen skills** (Nano-Banana, opc-logo-creator, opc-banner-creator, smart-illustrator, knowledge-card-generator, article-broll-illustrator, ecommerce-lp-generator, youtube-thumbnail, seedream-4-5):

**Input images speak louder than words** - Let reference images do the heavy lifting. Add text only for missing info.
- ❌ Bad: "A luxury red gift box with gold ribbon, Chinese New Year theme, 3D rendered..."
- ✅ Good: `【@图片1】luxury style, festive atmosphere`
- ✅ When image lacks info: `【@图片1】add gold ribbon, festive atmosphere`

See `/visual-prompt-engineer` for detailed guidance.

## NEW: Domain Mapping System

Complete domain and tag-based categorization of all skills. See [DOMAIN_GUIDE.md](references/DOMAIN_GUIDE.md) for full documentation.

### Quick Commands

```bash
# Regenerate domain mapping (after adding/modifying skills)
python3 scripts/regenerate_domain_map.py --verbose

# List all domains
python3 scripts/query_skills.py --list-domains

# List all tags
python3 scripts/query_skills.py --list-tags

# Query by domain
python3 scripts/query_skills.py --domain "Content Creation"

# Query by tags (OR logic)
python3 scripts/query_skills.py --tag python --tag youtube

# Query by tags (AND logic)
python3 scripts/query_skills.py --tag python --tag automation --all

# Query specific skill relationships
python3 scripts/query_skills.py --skill skill-orchestrator

# Interactive browser
python3 scripts/browse_domains.py
```

### 13 Primary Domains

1. **AI & ML** - AI models, machine learning, training
2. **Automation & Integration** - Workflow automation, API integration
3. **Business & Strategy** - Business planning, strategy, operations
4. **Content Creation** - Writing, research, copywriting
5. **Data & Research** - Data analysis, research, scraping
6. **Development** - Software development, coding tools
7. **E-Commerce** - Product management, marketing, sales
8. **Infrastructure & DevOps** - DNS, hosting, cloud
9. **Media & Design** - Images, video, audio, design
10. **Personal Development** - Coaching, learning, growth
11. **Productivity** - Task management, organization
12. **System & Meta** - Framework, documentation
13. **Web Development** - Frontend, backend, WordPress

### Tag System

- **Technology**: python, nodejs, go, bash, react, wordpress
- **Platform**: youtube, google, github, twitter, notion
- **Use Case**: research, generation, optimization, automation
- **Content Type**: text, image, video, audio, data

**Data File**: `references/skill_domain_map.json` (239 skills, 13 domains, 29 tags)

### Regenerating Domain Mapping

When skills are added, modified, or removed, regenerate the domain mapping:

```bash
python3 scripts/regenerate_domain_map.py --verbose
```

**What it does**:
1. Scans both `~/.gemini/antigravity/skills/` and `~/.claude/skills/`
2. Extracts metadata from each `SKILL.md` file
3. Classifies skills into domains using regex pattern matching
4. Extracts tags (technology, platform, use case, content type)
5. Identifies dependencies and output formats
6. Generates `skill_domain_map.json` (~165KB)

**Performance**: ~2 seconds for 239 skills

**Classification Logic**:
- **Domain**: Matches skill content against 13 domain patterns (AI & ML, Content Creation, etc.)
- **Tags**: Extracts 29 tags using regex patterns (python, youtube, automation, etc.)
- **Automatic**: No manual tagging required - reads from SKILL.md content

**When to regenerate**:
- After creating new skills
- After updating skill descriptions
- After renaming or moving skills
- Weekly for maintenance

See [DOMAIN_MAPPING_ACCELERATION.md](references/DOMAIN_MAPPING_ACCELERATION.md) for detailed guide.

## Core Capabilities

### 1. Relationship Discovery
Track which skills work together and form natural workflows.

```bash
python3 scripts/discover_relationships.py
```

Analyzes all skills to identify:
- Direct references (skill A mentions skill B in SKILL.md)
- Workflow chains (multi-step processes spanning skills)
- Shared domains (skills operating in same problem space)
- Tool dependencies (skills requiring same external tools)

**Output:** `references/skill_relationships.json`

### 2. Workflow Mapping
Document complete workflows that span multiple skills.

```bash
python3 scripts/map_workflows.py
```

Identifies workflow patterns:
- Sequential chains (A → B → C)
- Parallel operations (A + B → C)
- Conditional branches (A → B or C based on context)
- Feedback loops (A → B → A refinement)

**Output:** `references/workflows.md`

### 3. Design Language Audit
Ensure related skills share consistent tone, terminology, and structure.

```bash
python3 scripts/audit_design_language.py [workflow-name]
```

Checks for consistency in:
- Terminology (same concepts use same terms)
- Tone (formal vs casual, technical vs accessible)
- Structure (similar organization patterns)
- Output formats (compatible data structures)

**Output:** `references/design_audit_report.md`

### 4. Duplicate Analysis
Analyze duplicate and redundant skills with detailed comparison.

```bash
python3 scripts/analyze_duplicates.py
```

Identifies and analyzes:
- Symlink duplicates (pointing to external locations)
- Deprecated versions (superseded by newer skills)
- Content similarity (text overlap analysis)
- Structural differences (scripts, references, assets)

**Output:** `references/duplicate_analysis.md`

### 5. Overlap Documentation
Document functional overlaps between skill groups.

```bash
python3 scripts/document_overlaps.py
```

Analyzes skill groups:
- WordPress Management (15 skills)
- E-Commerce Landing Pages (2 skills)
- Image Enhancement (3 skills)
- Life Coaching (3 skills)

**Output:** `references/skill_overlaps.md`

### 6. Workflow Cooperation Mapping
Map how skills cooperate within parallel workflows.

```bash
python3 scripts/map_workflow_cooperation.py
```

Documents 4 parallel workflows:
- Writing Workflow (内容创作) - Research → Write → Refine → Distribute
- 配图 Workflow (Illustration/Visual) - Generate → Enhance → Export
- 剪辑 Workflow (Video Editing) - Transcribe → Edit → Generate → Optimize
- 网站 Workflow (Website Development) - Design → Code → Test → Deploy

**Output:** `references/workflow_cooperation.md`

### 7. Model Reference Scanner
Scan all skills for outdated AI model references.

```bash
python3 scripts/scan_model_references.py
python3 scripts/scan_model_references.py --update  # Update with permission
```

Integrates with model-intelligence to:
- Detect outdated model references (e.g., claude-sonnet-4-6 → 4-6)
- Filter false positives (CSS classes, tool names)
- Suggest upgrades for same model family
- Ask permission before updating skill files

**Output:** `references/model_scan_YYYYMMDD_HHMMSS.log`

### 8. Category Index Generation
Organize all skills into browsable categories.

```bash
python3 scripts/generate_category_index.py
```

Creates index with 10 categories:
- Content Creation (40 skills)
- Visual & Media Production (41 skills)
- Web & App Development (37 skills)
- E-Commerce & Business (24 skills)
- Data & Research (14 skills)
- Productivity & Automation (17 skills)
- Personal Development (14 skills)
- Infrastructure & DevOps (11 skills)
- AI & Model Integration (12 skills)
- Meta & System (15 skills)

**Output:** `~/.gemini/antigravity/skills/CATEGORIES.md`

## Quick Commands

### Query Skills
```bash
# List all domains
python3 scripts/query_skills.py --list-domains

# List all tags
python3 scripts/query_skills.py --list-tags

# Query by domain
python3 scripts/query_skills.py --domain "Content Creation"

# Query by tags (OR logic)
python3 scripts/query_skills.py --tag python --tag youtube

# Query by tags (AND logic)
python3 scripts/query_skills.py --tag python --tag automation --all

# Query specific skill relationships
python3 scripts/query_skills.py --skill skill-orchestrator

# Interactive browser
python3 scripts/browse_domains.py
```

### Review Duplicates
```bash
python3 scripts/analyze_duplicates.py
```
Generates detailed comparison of duplicate skill candidates.

### Browse by Category
```bash
cat ~/.gemini/antigravity/skills/CATEGORIES.md
```
Browse all skills organized by category.

### View Workflow Cooperation
```bash
cat references/workflow_cooperation.md
```
See how skills cooperate within the 4 parallel workflows.

### Check Skill Overlaps
```bash
cat references/skill_overlaps.md
```
Understand functional overlaps between skill groups.

## Relationship Types

**Direct Dependencies:** Skill A explicitly calls or references Skill B.
- Example: `ecommerce-lp-generator` → `performance-ads-writer`

**Workflow Chains:** Skills that naturally follow each other in multi-step processes.
- Example: `honest-deep-researcher` → `content-research-writer` → `performance-ads-writer`

**Domain Clusters:** Skills operating in the same problem space.
- Example: All WordPress skills (`wp-*`) form a cluster

**Tool Ecosystems:** Skills sharing external dependencies.
- Example: All Notion skills require `notion-mcp-connector`

## Design Language Profiles

Each workflow defines its design language:

**Technical/Formal:** Precise terminology, structured output, minimal personality
- Example workflows: GSD framework, WordPress development

**Creative/Casual:** Conversational tone, flexible structure, personality-driven
- Example workflows: Content creation, social media

**Business/Strategic:** Executive summary style, data-driven, action-oriented
- Example workflows: Market research, business planning

## Examples

### Example 1: Discover Content Creation Workflow
```bash
python3 scripts/query_relationships.py content-research-writer
# Shows: honest-deep-researcher, performance-ads-writer, youtube-title, social-media-*
```

### Example 2: Audit E-commerce Workflow Consistency
```bash
python3 scripts/audit_design_language.py ecommerce-workflow
# Identifies terminology mismatches, tone inconsistencies, structure differences
```

### Example 3: Execute Research-to-Content Workflow
```bash
python3 scripts/execute_workflow.py research-to-content \
  --params topic="AI trends 2026" output_format="blog_post"
```

## Integration with Other Skills

**With `skill-creator`:** Run relationship discovery after creating new skills to identify connections.

**With `skill-improver`:** Use design language audit to ensure consistency before improvements.

**With `skill-lookup`:** Query relationships to find complementary skills.

## Agent Integration Notes

**Discovery phase:** Run relationship discovery after installing new skills
**Planning phase:** Query workflows before starting multi-step tasks
**Execution phase:** Use workflow execution for orchestrated operations
**Audit phase:** Run design language audit periodically

**Proactive usage:** Run discovery weekly or after batch skill installations.
