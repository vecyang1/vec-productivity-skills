# Changelog

All notable changes to `yopu-cli` (`yp`) will be documented in this file.

## [1.2.0] - 2026-10-10

### Added
- **API v2 Token Algorithm (`compute_sheet_t`)**: Reverse-engineered Yopu v2 token encryption from `data-model.st` (W-permutation and XOR 22-byte cycle with key `SdZWq_H3OXnrFgPLwk9kow`) to unlock full sheet data bypassing preview paywalls.
- **Auto-Authentication & 1Password Integration**: Automatic credential ingestion from 1Password (`Agent Automation` vault) and local Chrome SQLite cookie databases (`Profile 2` / `Default`) with `~/.config/yopu/cookies.json` caching and explicit `yp --refresh-auth` support.
- **Direct Lead Sheet Auto-Download**: Running `yp <url_or_id>` now automatically persists cleanly stripped plain text (`[Title] - [Artist].txt`) or markdown (`-f md`) to the current directory.
- **Selectable Vector PDF Generation**: Added `--pdf` and `-f pdf` flags delegating directly to sister tool `yopu-pdf` using pinned Python 3.12 runtime.
- **CJK East Asian Width Visual Alignment**: Implemented display width calculation via `unicodedata.east_asian_width` to ensure chord tokens align perfectly above Chinese/Japanese lyrics in monospace environments.
- **Pickup Note & Dual-Track Parsing**: Support for pickup notes (`cut_bi`), accompaniment track chords (`r8q`, `i1f`), and vocal melody track lyrics (`t2g[1]`).

## [1.1.0] - 2026-10-02

### Added
- Documented zero-facade browser fallback protocol via `chrome-devtools` for environments where direct CLI urllib requests are blocked by Yopu's edge TLS fingerprint gate.
- Documented Svelte SVG DOM chord and lyric text extraction pattern from `#nier-scroll-view svg`.

## [1.0.0] - 2026-08-27

### Added
- Initial release of `yopu-cli` (`yp`).
- Resilient HTML fetcher for Yopu score URLs and raw IDs.
- Core score parser with section header detection, chord token extraction, and lyric alignment.
- Full chromatic music theory engine supporting transposition by semitones, target keys, and capo adjustment.
- Multiple export formats: Terminal (colored), ChordPro, Markdown, Plain Text, and JSON.
- 11 unit tests with automated test runner.
- AGPL-3.0 licensing and documentation.
