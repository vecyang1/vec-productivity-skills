# Changelog

## [1.3.0] - 2026-03-05
### Added
- **Skill Cleaning Mode**: New `--clean` flag for preparing skills for public sharing
  - Removes API tokens, secrets, and credentials (OpenAI, Notion, Bearer tokens)
  - Sanitizes personal paths and usernames (`/Users/username/` → `/Users/your_username/`)
  - Replaces database IDs with placeholders (Notion IDs, UUIDs)
  - Removes personal data (emails, identifiers)
  - Generates template files (`.env.example`, `databases.md.template`, `config.example.json`)
  - Creates detailed cleaning report showing all changes
  - Dry-run mode (`--dry-run`) for preview without modifications
  - Automatic backup creation
  - Custom output directory support (`--output`)
- **Safety Features**:
  - Original skill never modified (unless `--in-place` flag used)
  - Skips binary files and already-templated files
  - Preserves file structure and functionality
- **Documentation**: Added Phase 1.5 to SKILL.md with cleaning workflow

### Enhanced
- Extended security scanning patterns for better token detection
- Improved path detection for cross-platform support (macOS, Linux)
- Added auto-detection of username from path patterns

## [1.2.3] - 2026-02-28
### Self-Improvement (Recursive Evolution)
- **Phase 6 Enhancement**: Added Memory Integration Check — skill-improver now detects if target skills work with recurring user contexts and injects `memory:context-vault` usage hint when appropriate.

## [1.2.2] - 2026-02-26
### Self-Improvement (Recursive Evolution)
- **Pattern Recognition**: Discovered that RL training skills benefit from extended reference documentation (REFERENCES.md, TROUBLESHOOTING.md, HYPERPARAMETER_TUNING.md) to follow Token Economy principle.
- **Lesson Learned**: When improving documentation-heavy skills, move verbose content to `references/` folder to keep main SKILL.md concise but comprehensive.
- **Applied To**: Successfully improved `rl-training-ppo` skill with proper structure, principles, self-evolution protocol, and extended documentation.

## [1.2.1] - 2026-02-06
- Added `--fix` flag to `audit_skill.py` to automatically inject missing standard sections (Principles, Self-Evolution) and create `CHANGELOG.md`.

## [1.2.0] - 2026-02-06
### Added
- **Autopoiesis (The Living Form)**: Added Phase 6 to inject a "Self-Evolution Protocol" into every improved skill.
- **Protocol**: Mandates that agents check for high-signal improvements before ending sessions.
- **Principles Injection**: Added mandate to inject specific "Principles" section.
- **Systemic Inheritance**: Configured `skill-improver` to dynamically read its own current principles (from `SKILL.md`) and stamp them onto improved skills, ensuring the "Soul" of the system evolves and propagates automatically.
- **Audit Update**: Updated `audit_skill.py` to check for the presence of the "Principles" section.

## [1.1.0] - 2026-02-06
### Added
- **Principle**: Enforced "Token Economy". Instructions for moving bulky setup steps to `references/setup.md` to keep `SKILL.md` lean.

## [1.0.1] - 2026-02-06
- Renamed skill from `skill-improve` to `skill-improver`.
- Refined `check_runtime_imports` to act as a "Disk Space Guardian".
- Defined workflow for auditing, improving, and consolidating agent skills.
- Added strict requirements for source traceability and script consolidation.
- Added "Phase 6: Recursive Evolution" to `SKILL.md` to enforce self-improvement.
- Updated `audit_skill.py` with extension slots for future checks.
- [Self-Improvement] Added `check_security_hygiene` to `audit_skill.py` to count for hardcoded API keys and missing .env.example files (learned from mcp-flight-search).
- [Self-Improvement] Added `check_dependencies` to `audit_skill.py` to warn if `requirements.txt` is missing when imports like `requests` or `openai` are used (learned from Nano-Banana-Pro).
- [Self-Improvement] Refined `check_runtime_imports` to act as a "Disk Space Guardian". Added explicit size estimates (~MB/GB) for heavy libraries and added warnings against installing them for rarely used skills.
