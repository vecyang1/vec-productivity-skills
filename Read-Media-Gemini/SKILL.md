---
name: Read-Media-Gemini
description: A specialized skill for Gemini 3 Flash and other models via Antigravity Local Proxy. Optimized for multimodal understanding. Supports local files, Google Drive URLs, and YouTube URLs. For spatial reasoning, counting, zooming, or programmatic image analysis, delegates to agentic-vision-gemini (agentic mode with code execution).
version: 2.3.0
author: System
---

# Read-Media-Gemini (Multimodal - Antigravity Edition)

This skill uses Vector Engine (向量引擎) as the primary provider to avoid proxy-triggered account flags. Falls back to Kie AI and Google Direct if unavailable.

## Supported File Sources

### 1. Local Files
Standard filesystem paths:
```bash
./scripts/run.sh "Describe" --file "/path/to/video.mp4"
```

### 2. Google Drive URLs
Direct integration with Google Drive API:
```bash
# Full URL
./scripts/run.sh "Describe" --file "https://drive.google.com/file/d/1ABC...XYZ/view"

# Direct file ID
./scripts/run.sh "Transcribe" --file "1ABC...XYZ"
```

**Authentication** (tried in order):
1. **gcloud**: `~/.config/gcloud/application_default_credentials.json`
2. **OAuth**: `~/.gemini/oauth_creds.json` (browser auth on first use)
3. **Token cache**: `~/.gdrive_token.json` (auto-saved)

**Supported formats**:
- `https://drive.google.com/file/d/FILE_ID/view`
- `https://drive.google.com/open?id=FILE_ID`
- Direct file ID: `FILE_ID` (25+ chars)

### 3. Google Cloud Storage (GCS) URIs
**Note**: GCS URIs (`gs://bucket/path/file.mp4`) are **NOT directly supported** by this skill.

To use GCS files:
1. Download locally first: `gsutil cp gs://bucket/file.mp4 /tmp/file.mp4`
2. Then analyze: `./scripts/run.sh "Describe" --file "/tmp/file.mp4"`

**Why?** The Gemini File API requires either:
- Local file upload → generates `https://generativelanguage.googleapis.com/v1beta/files/...` URI
- Pre-existing GCS URI (only works with Vertex AI, not Gemini Developer API)

This skill uses Gemini Developer API (via Antigravity proxy), which doesn't support direct GCS URIs.

### 4. YouTube URLs
**Supported via Gemini File API!** YouTube URLs can be passed directly:
```bash
./scripts/run.sh "Summarize this video" --file "https://www.youtube.com/watch?v=VIDEO_ID"
./scripts/run.sh "What is this about?" --file "https://youtu.be/VIDEO_ID"
```

**Supported formats**:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://youtube.com/shorts/VIDEO_ID`

**Provider routing**: Automatically uses Google Direct (Vector Engine/Kie AI don't support YouTube URLs directly)

**Requirements**: Video must be public and not geo-restricted

**Model used**: `gemini-3-flash-preview` (latest Flash model as of 2026-03-01)

## Mode Routing — Standard vs Agentic

| Task | Use | Command |
|------|-----|---------|
| Describe / summarize image | **This skill** (standard) | `./scripts/run.sh "Describe" --file img.jpg` |
| Transcribe audio / video | **This skill** (standard) | `./scripts/run.sh "Transcribe" --file audio.mp3` |
| Count objects, zoom into region | **agentic-vision-gemini** | requires `GEMINI_API_KEY` (Google Direct) |
| Measure / crop / pixel analysis | **agentic-vision-gemini** | Kie cannot support — no code execution sandbox |
| Read serial numbers / fine text | **agentic-vision-gemini** | Kie cannot support — verified 2026-02-24 |
| Compare two images for differences | **agentic-vision-gemini** | multi-image support |

**Rule**: If the task requires spatial reasoning, iteration, or programmatic image manipulation → delegate to `agentic-vision-gemini`:

```bash
python3 ~/.gemini/antigravity/skills/agentic-vision-gemini/scripts/agentic_vision.py \
  --image "/path/to/image.jpg" \
  --prompt "Zoom into the label and read the serial number"
```

See full agentic docs: `~/.gemini/antigravity/skills/agentic-vision-gemini/SKILL.md`

## Capabilities

-   **Antigravity Proxy Integration**: Connects directly to your local model proxy.
-   **Provider Priority**:
    1.  **Vector Engine** (Primary — `api.vectorengine.ai`, official Gemini SDK compatible)
    2.  **Kie AI** (Alternative — `api.kie.ai`, OpenAI-compatible, images only)
        - Skipped automatically for: videos, YouTube URLs, Google Drive URLs
    3.  **Google Direct** (Fallback — supports images + video + YouTube via File API)
        - Used for: all videos, YouTube URLs, Google Drive files
    4.  Antigravity Proxy (last resort)
-   **Multimodal Support**: Seamlessly handles Images, Video, Audio, and YouTube URLs.
-   **Video Optimization**: Automatically compresses local videos to 720p@20fps for faster processing.
-   **Smart Routing**: Detects file type and source, routes to appropriate provider automatically.

## Prerequisites

> **`/Applications/Antigravity Tools.app` must be running** before using this skill (provides the local proxy at port 8045).
> Auto-check: `pgrep -f "Antigravity Tools" || open "/Applications/Antigravity Tools.app"`

## Configuration

Required Environment Variables in `.env`:
-   `PRIMARY_PROVIDER`: `vectorengine` (default) or `kie`
-   `VECTORENGINE_API_KEY`: Your Vector Engine API key.
-   `ANTIGRAVITY_API_KEY`: Your Antigravity API key.
-   `ANTIGRAVITY_BASE_URL`: Proxy URL (default: `http://127.0.0.1:8045`).

## Usage Examples

```bash
# Local Image Analysis
./scripts/run.sh "Describe this image" --file "image.jpg"

# Google Drive Video
./scripts/run.sh "Summarize this video" --file "https://drive.google.com/file/d/1ABC...XYZ/view"

# Multi-file Analysis (local + Drive)
./scripts/run.sh "Compare these videos" \
  --file "local_video.mp4" \
  --file "https://drive.google.com/file/d/1ABC...XYZ/view"

# Audio Transcription from Drive
./scripts/run.sh "Transcribe this audio" --file "https://drive.google.com/file/d/1ABC...XYZ/view"

# YouTube (download first)
yt-dlp -o /tmp/yt.mp4 "https://youtube.com/watch?v=..." && \
./scripts/run.sh "Describe" --file "/tmp/yt.mp4"
```

## 🧬 Self-Evolution (Autopoiesis)

**Post-Task Reflection**:
Before ending the session, the Agent MUST ask: "Did I learn a new pattern, fix a bug, or add a critical feature?"
-   **YES**: Log it in `CHANGELOG.md` and update `SKILL.md` / `references/` immediately.
-   **NO**: Do nothing.
-   **Constraint**: Only log **High-Signal** improvements.
