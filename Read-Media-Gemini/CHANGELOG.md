# Changelog

## [2.3.0] - 2026-03-01
### Added
- **YouTube URL Support**: Direct YouTube video analysis without download
  - Accepts YouTube URLs: `youtube.com/watch?v=`, `youtu.be/`, `youtube.com/shorts/`
  - Uses Gemini's native YouTube support via `Part.from_uri()`
  - No download required - video must be public and not geo-restricted
  - Discovered via community MCP: `yt-analysis-mcp` by Legorobotdude

### Changed
- Updated `scripts/chat.py` with YouTube URL detection and direct URI passing
- Modified `load_media_items()` to accept `youtube_urls` parameter
- **Provider routing**: Automatically skips Kie AI when YouTube URLs detected (Kie doesn't support YouTube)
- **Model priority updated**: Now uses `gemini-3-flash-preview` (latest) → `gemini-2.5-flash` (fallback)
  - Removed deprecated: `gemini-3-flash`, `gemini-3-pro-high`
- Updated `SKILL.md` to document YouTube URL support and provider routing logic

### Fixed
- Kie AI no longer hangs on YouTube URLs - now falls through to Google Direct immediately

## [2.2.0] - 2026-03-01
### Added
- **Google Drive Support**: Merged functionality from deleted `gdrive-gemini-analyzer` skill.
  - Accepts Google Drive URLs as `--file` arguments (e.g., `https://drive.google.com/file/d/FILE_ID/view`)
  - Auto-detects Drive URLs vs local paths — seamless handling
  - Authentication via gcloud → OAuth (`~/oauth_creds.json`) → cached token (`~/.gdrive_token.json`)
  - Downloads Drive files to temp directory, processes them, then auto-cleans up
  - Supports all Drive URL formats: full URL, open URL, or direct file ID
- Added Google Drive API dependencies to `requirements.txt`: `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`

### Changed
- Updated `scripts/chat.py` with Drive URL detection, file ID extraction, credential management, and download logic
- Updated `SKILL.md` to document Google Drive support with usage examples
- Bumped version to 2.2.0

### Documentation
- **Clarified file source support** in SKILL.md:
  - ✅ Local files (filesystem paths)
  - ✅ Google Drive URLs (via Drive API integration)
  - ❌ GCS URIs (`gs://...`) - NOT supported (requires Vertex AI, not Gemini Developer API)
  - ❌ YouTube URLs - NOT supported (must download with yt-dlp first)
- Added technical explanation: Gemini File API requires local upload or pre-existing GCS URI (Vertex AI only)
- This skill uses Gemini Developer API via Antigravity proxy, which doesn't support direct GCS URIs

## [2.1.0] - 2026-02-24
### Added
- **Agentic Mode Routing**: Added mode routing table to SKILL.md — standard multimodal tasks stay in this skill; spatial/programmatic image tasks (count, zoom, crop, measure) delegate to `agentic-vision-gemini`.
- Updated `description` frontmatter to reflect agentic delegation.

## [2.0.0] - 2026-02-12
### Added
- **Antigravity Proxy Integration**: Now uses local proxy (`http://127.0.0.1:8045`) via `google-generativeai` SDK as the primary provider.
- **Hybrid Fallback System**: Implemented a 3-tier fallback strategies: Antigravity Proxy (SDK) -> Kie (Requests) -> Google Direct (SDK).
- **Video Optimization**: Ported video compression logic (ffmpeg) to the new SDK implementation.
- **Model Priority**: Configured priority list: `gemini-3-flash`, `gemini-3-pro-high`, `claude-sonnet-4-5-thinking`.

### Changed
- Rewrote `scripts/chat.py` to utilize `google-generativeai` SDK for primary operations.
- Updated `.env` structure to support legacy keys alongside new proxy configuration.
- Bumped version to 2.0.0 due to major architectural change (switching primary SDK).

## [1.3.0] - 2026-02-12
### Added
- Added provider router in `scripts/chat.py` with Kie-first priority and automatic Google fallback.
- Added explicit multi-reference request support across providers (repeatable `--file` handling).
- Added test suite in `tests/test_chat_router.py` covering:
  - Kie prioritized path
  - Kie failure -> Google fallback
  - Multi-image payload construction
  - No-key failure behavior

### Changed
- Updated `SKILL.md` to document Kie priority, Google fallback, and multi-image usage examples.
- Updated `references/setup.md` and `.env.example` with dual-provider configuration and defaults.

## [1.1.0] - 2026-02-06
### Security
- **CRITICAL**: Removed hardcoded API key from `scripts/chat.py`. Now loads strictly from environment variables or `.env`.
- Added `.env` and `.env.example` for secure configuration.

### Added
- Added `requirements.txt` specifically for this skill (requests, python-dotenv).

### Changed
- Refactored `scripts/chat.py` to use `python-dotenv`.
- Updated `SKILL.md` with new configuration instructions and source attribution.
- **Optimization**: Added `scripts/run.sh` to implement lazy-loading Virtual Environment (`.venv`). Dependencies are now installed only once into a local subfolder, accelerating subsequent runs and saving agent tokens.
- **Autopoiesis**: Injected "Self-Evolution Protocol" to enforce continuous improvement.

## [1.0.0] - 2026-01-22
### Added
- Initial release of `Kie-Gemini-3-Flash`.
- `scripts/chat.py`: Main interaction script supporting Text, Image, Video, and Audio inputs.
- Implemented automatic mime-type detection and `input_audio` support for audio files.
- Verified support for `.mp4` video analysis and `.mp3` audio transcription/summarization.
- Integrated `KIE_API_KEY` with fallback to default key.

## [2.3.1] - 2026-03-09
### Added
- Added support for **Vector Engine (向量引擎)** (`api.vectorengine.ai`) as the primary fast provider.
- Integrated `gemini-3-flash-preview` seamlessly with the Vector Engine via the Gemini Developer API SDK structure.
- Expanded fallback logic to cascade: Vector Engine -> Kie AI -> Google Direct -> Antigravity Proxy.
