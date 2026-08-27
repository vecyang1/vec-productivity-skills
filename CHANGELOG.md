# Changelog

All notable changes to Vec's Productivity Skills will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **License: MIT → AGPL-3.0-or-later** (2026-08-17). Copies obtained before this
  date keep their MIT grant; it is not revoked. `skill-creator/` (Apache-2.0),
  `skill-improver/` (MIT) and `notion-mcp-connector/` (MIT) keep their own
  LICENSE files and are not relicensed — see [NOTICE](./NOTICE).

### Added
- **Yopu CLI ( / )**: Production-ready CLI and Python SDK for fetching, parsing, transposing, and exporting guitar & ukulele chord sheets from Yopu.co (有谱么).
  - Fetches scores by URL or score ID with anti-blocking headers.
  - Full chromatic music theory engine supporting transposition by semitones, target keys, and capo adjustment.
  - Multi-format export: Terminal lead sheet, ChordPro standard, Markdown, Plain Text, and JSON.
  - 11 unit tests covering transposition, parsing, and formatting.
  - Licensed under AGPL-3.0.
- **OpenSky Network CLI (`opensky-network-cli`)**: Production-ready CLI and Python SDK for the OpenSky Network REST API.
  - Live aircraft radar telemetry (`/states/all`), bounding-box / callsign / country filters, velocity / altitude / vertical rate parsing.
  - Airport arrival/departure flight tracking (`/flights/*`) and aircraft trajectory waypoints (`/tracks/all`).
  - OAuth2 Client Credentials lifecycle with automatic 30-minute token caching, live `X-Rate-Limit-Remaining` daily credit accounting (4,000 credits/day standard tier), and transparent public DNS fallback (`1.1.1.1` / `8.8.8.8`).
  - 1Password automated credential resolution (`op://Agent Automation/OpenSky Network/username`) with graceful fallback to anonymous mode.
  - 6 deterministic offline unit tests with 0 network dependency.
- **Squirrly SEO Operations**: multi-brand CLI over the undocumented Squirrly
  SEO cloud API (`api.squirrly.co/v2`), with 76 endpoint/verb pairs mapped from
  the vendor's WordPress plugin source and confirmed against the live server.
  - Credential lane stores pointers only — `env://VAR`, or `op://` through a
    1Password Service Account bridge that refuses the interactive route rather
    than silently working while a human is at the keyboard.
  - Writes need `--confirm` *and* a per-brand `allow_writes`; quota-spending
    GETs (`posts.crawl`, `serp.refresh`) and state-rotating ones
    (`user.dashboardlink`, `user.token`) are marked mutating despite the verb.
  - Entitlement-blocked endpoints keep a `gate` and a reason instead of being
    dropped, so a plan limit is never misread as a missing capability.
  - 105 hermetic unit tests; `scripts/e2e_check.py` is a 10-stage live gate
    proven red-capable by mutation.
- **Post Social Media with Zernio API**: Community-safe direct publishing skill with exact-account preflight, caption-preserving dry runs, explicit publish confirmation, idempotent request receipts, and a deterministic privacy gate for working trees and reachable Git history.
- **Feishu / Lark CLI Operator**: Routing and safety skill for the official `lark-cli` across Docs, Drive, Base, Sheets, Wiki, and Markdown.
  - Auth baselines for user vs. bot identity, plus the `--no-wait` / `--device-code` login flow for agent harnesses that cannot block on a browser.
  - Intent → command routing paired with the CLI's embedded, version-matched skills (`lark-cli skills read <name>`), which outrank any local copy on flag details.
  - High-risk-write contract verified against the CLI: exit `10` with `error.subtype == "confirmation_required"` means request approval; never auto-retry with `--yes`.
  - Corrects prior guidance that `docs` commands must pass `--api-version v2`. Verified inert on current builds — the flag parses but yields a byte-identical dry-run payload and endpoint. Documents the dry-run diff technique for distinguishing honoured flags from ignored ones.
  - Output-handling rules: `--dry-run` payloads embed `app_id` and `user_open_id` and are not safe to paste into public issues verbatim.
  - Version-independent `lark-cli` wrapper that resolves npm's `npx-cli.js` through the active Node runtime instead of a hardcoded install path.

## [1.1.0] - 2026-06-19

### Added
- **Yopu CLI ( / )**: Production-ready CLI and Python SDK for fetching, parsing, transposing, and exporting guitar & ukulele chord sheets from Yopu.co (有谱么).
  - Fetches scores by URL or score ID with anti-blocking headers.
  - Full chromatic music theory engine supporting transposition by semitones, target keys, and capo adjustment.
  - Multi-format export: Terminal lead sheet, ChordPro standard, Markdown, Plain Text, and JSON.
  - 11 unit tests covering transposition, parsing, and formatting.
  - Licensed under AGPL-3.0.
- **Scheduled Task Rescheduler**: Safely reschedule, rename, rebuild, split, or merge recurring agent tasks (Antigravity, Codex, Claude Code, LaunchAgent, cron, n8n) without losing checkpoints, success markers, runtime IDs, output owners, or catch-up policy. Treats the scheduler trigger as an alarm clock and a durable Markdown cadence card as the source of truth.
  - Reschedule/rebuild lineage rules with worked examples (rename, new-ID, split, merge, runtime swap).
  - Antigravity two-layer activation reference (`sidecar.json` + `config.json` + `projects/<id>.json`) with a verification gate.
  - Catch-up, retry, and midnight-credit policy guidance.
  - Copyable cadence-card template with full field and status vocabulary.
  - Zero-dependency `validate_cadence_card.py` (Python stdlib): checks required fields, status vocabulary, incremental-state completeness, and alias↔execution-root agreement. Fence-aware parsing so headings inside code blocks are skipped; covered by a stdlib `unittest` suite under `tests/`.

## [1.0.0] - 2026-03-05

### Added
- **Yopu CLI ( / )**: Production-ready CLI and Python SDK for fetching, parsing, transposing, and exporting guitar & ukulele chord sheets from Yopu.co (有谱么).
  - Fetches scores by URL or score ID with anti-blocking headers.
  - Full chromatic music theory engine supporting transposition by semitones, target keys, and capo adjustment.
  - Multi-format export: Terminal lead sheet, ChordPro standard, Markdown, Plain Text, and JSON.
  - 11 unit tests covering transposition, parsing, and formatting.
  - Licensed under AGPL-3.0.
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
