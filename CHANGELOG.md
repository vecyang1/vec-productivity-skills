# Changelog

All notable changes to Vec's Productivity Skills will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-06-19

### Added
- **Scheduled Task Rescheduler**: Safely reschedule, rename, rebuild, split, or merge recurring agent tasks (Antigravity, Codex, Claude Code, LaunchAgent, cron, n8n) without losing checkpoints, success markers, runtime IDs, output owners, or catch-up policy. Treats the scheduler trigger as an alarm clock and a durable Markdown cadence card as the source of truth.
  - Reschedule/rebuild lineage rules with worked examples (rename, new-ID, split, merge, runtime swap).
  - Antigravity two-layer activation reference (`sidecar.json` + `config.json` + `projects/<id>.json`) with a verification gate.
  - Catch-up, retry, and midnight-credit policy guidance.
  - Copyable cadence-card template with full field and status vocabulary.
  - Zero-dependency `validate_cadence_card.py` (Python stdlib): checks required fields, status vocabulary, incremental-state completeness, and alias↔execution-root agreement.

## [1.0.0] - 2026-03-05

### Added
- Initial release of unified skills collection
- **Agent Teams Dashboard**: Team management and coordination system
- **Skill Improver**: Meta-skill for skill quality assurance
- **Notion MCP Connector**: Comprehensive Notion integration
- Unified repository structure
- Comprehensive documentation for all skills
- MIT License for all skills

### Changed
- Consolidated individual skill repositories into single collection
- Standardized documentation format across all skills
- Improved installation and usage instructions

### Security
- Removed all hardcoded API tokens and credentials
- Added environment variable configuration
- Implemented GitHub secret scanning compliance

## Future Plans

### Planned Features
- Additional skills for common workflows
- Enhanced cross-skill integration
- Automated testing framework
- Community contribution guidelines
- Skill templates and generators

### Under Consideration
- Web-based skill browser
- Skill dependency management
- Performance benchmarking tools
- Integration with popular development tools

---

For detailed changes in individual skills, see their respective CHANGELOG.md files.
