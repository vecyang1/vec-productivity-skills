# Changelog

All notable changes to the skill-orchestrator skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-03-07

### Fixed
- **CRITICAL**: Fixed model scanner bug - changed `skill.md` to `SKILL.md` (case sensitivity issue)
- Model scanner now correctly finds all skills instead of zero

### Changed
- **BREAKING**: Consolidated 3 query tools into unified `query_skills.py`
  - Replaced `query_by_domain.py`, `query_relationships.py`, `browse_domains.py`
  - Single tool with `--domain`, `--tag`, `--skill`, `--list-domains`, `--list-tags` flags
  - Maintains all functionality with cleaner interface
- Extracted shared metadata extraction logic into `_metadata_extractor.py`
  - Eliminates ~150 lines of duplicated code
  - Used by both `regenerate_domain_map.py` and `discover_relationships.py`
  - Ensures consistent metadata parsing across all tools

### Removed
- `query_by_domain.py` - replaced by `query_skills.py`
- `query_relationships.py` - replaced by `query_skills.py`
- `register_manual_relationships.py` - orphaned, unused script

### Updated
- Regenerated stale data files (domain_map.json, skill_relationships.json)
- Updated SKILL.md documentation to reflect new unified query tool
- Reduced script count from 14 to 12 (14% reduction)

### Performance
- Metadata extraction now shared across tools (DRY principle)
- Query operations unified for better maintainability
- Reduced maintenance surface by consolidating overlapping functionality

## [1.1.0] - 2026-03-02

### Added
- Duplicate analysis system (`analyze_duplicates.py`)
  - Analyzes 5 duplicate/redundant skill candidates
  - Compares symlink duplicates, deprecated versions
  - Calculates content similarity scores
  - Provides deletion recommendations with impact analysis
- Overlap documentation system (`document_overlaps.py`)
  - Documents functional overlaps for 4 skill groups
  - WordPress Management (15 skills)
  - E-Commerce Landing Pages (2 skills)
  - Image Enhancement (3 skills)
  - Life Coaching (3 skills)
  - Generates capability matrices and use case boundaries
- Workflow cooperation mapping (`map_workflow_cooperation.py`)
  - Maps 4 parallel workflows with cooperation chains
  - Writing Workflow (内容创作) - 25 skills
  - 配图 Workflow (Illustration/Visual) - 29 skills
  - 剪辑 Workflow (Video Editing) - 11 skills
  - 网站 Workflow (Website Development) - 38 skills
  - Documents entry points and integration points
- Category index generation (`generate_category_index.py`)
  - Organizes 225 skills into 10 categories
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
  - Generates browsable index at `~/.gemini/antigravity/skills/CATEGORIES.md`

### Changed
- Updated SKILL.md with new analysis capabilities
- Enhanced documentation with workflow cooperation examples
- Added quick reference commands for new reports

### Reports Generated
- `references/duplicate_analysis.md` - Detailed duplicate skill comparison
- `references/skill_overlaps.md` - Functional overlap documentation
- `references/workflow_cooperation.md` - Workflow cooperation maps
- `~/.gemini/antigravity/skills/CATEGORIES.md` - Browsable category index

## [1.0.0] - 2026-03-02

### Added
- Initial release of skill-orchestrator
- Relationship discovery system (`discover_relationships.py`)
- Workflow mapping system (`map_workflows.py`)
- Design language audit system (`audit_design_language.py`)
- Relationship query tool (`query_relationships.py`)
- Support for tracking:
  - Direct skill references
  - Domain clusters (skills in same problem space)
  - Tool ecosystems (skills sharing dependencies)
  - Workflow chains (sequential, parallel, conditional)
- Design language profiles (Technical/Formal, Creative/Casual, Business/Strategic)
- Known workflow patterns:
  - Content Creation Pipeline
  - E-commerce Product Launch
  - WordPress Development Workflow
  - Video Content Production
  - Research to NotebookLM Artifacts

### Features
- Automatic relationship discovery from SKILL.md files
- Tone analysis (formal vs casual vs technical)
- Terminology consistency checking
- Structure pattern analysis
- Workflow chain detection
- Domain clustering
- Tool ecosystem mapping

## 2026-03-04 - Skill Cleanup

### Deleted
- **geo** - Redundant with `opc-seo-geo`
  - Reason: `opc-seo-geo` is more comprehensive (covers both SEO + GEO, platform-specific optimization for 5 AI engines, research-backed with Princeton study, includes audit tools and schema templates)
  - `geo` only covered basic GEO workflow without SEO integration

