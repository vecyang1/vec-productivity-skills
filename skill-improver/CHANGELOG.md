# Changelog

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
