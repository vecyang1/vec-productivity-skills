---
name: transcribe-media
description: Transcribe video or audio files into text using Google's Gemini 3 Flash. Preserves original language, identifies speakers, cleans noise, and formats for readability without timestamps.
---

# Transcribe Media (Migrated to Google API)

This skill transcribes video and audio files into readable text using Google's official Gemini API. It preserves the original language (or Simplified Chinese if applicable), removes timestamps, and identifies speakers.

**Note:** Support for Kie.ai hosted Gemini 3 Flash has been sunset. This skill now uses `GOOGLE_API_KEY`.

## Capabilities

- **Video/Audio Transcription**: Supports common video and audio formats.
- **Noise Cleaning**: Removes invalid fragments while keeping the original transcription intact.
- **Formatting**: Outputs easy-to-read text with necessary paragraph and line breaks.
- **Speaker Identification**: Identifies speakers by name (if discernible) or labels (Speaker 1, etc.).
- **No Timestamps**: Clean output without timecodes.
- **Objective Output**: Defaults to `temperature=0.0` for maximum accuracy.

## Usage

Use this skill when the user wants to transcribe a media file.

### Prerequisites

- The video or audio file must be accessible locally or via a URL.
- Python 3 and ffmpeg (for video compression) are required.
- **Google API Key** configured in `.env`.

### Instructions

To transcribe a single file, run the `scripts/transcribe.py` script with the specific prompt designed for this task.

```bash
python3 scripts/transcribe.py "Transcribe the video/audio into text; Output in its in original language. include speaker name. no timestamp. output all. easy to read. Add necessary paragraph break, line break, 保持所有transcribe原文, 同时清洗无效片段. if it's chinese, use simplified Chinese." --file "/absolute/path/to/media/file" --type video
```

### Batch Processing

To process multiple files in parallel (e.g., 1000 MP3s), use the `--dir` flag. Parallel processing uses exponential backoff to handle rate limits efficiently. You can set the number of concurrent threads using `--workers` (default is 5). Processed files will be skipped automatically on subsequent runs if the output `.txt` exists.

```bash
python3 scripts/transcribe.py "Transcribe the audio into text..." --dir "/absolute/path/to/folder_with_mp3s" --type audio --workers 10
```

**Note:**
- Replace paths with your actual paths.
- For batch processing, parsed output is saved as `<filename>.txt` automatically.
- Use `--type audio` for audio-only files (mp3, wav).

## Configuration

- **API Key**: Uses `VECTORENGINE_API_KEY` (Default Priority 1) or `GOOGLE_API_KEY` (Priority 2) environment variables.
- **Model**: Uses `gemini-3.1-flash-lite-preview` (default) or configured via `TRANSCRIBE_MODEL`.

## Changelog
- **2026-03-13** (V) - Refactored `scripts/transcribe.py` for parallel batch processing (`--dir` / `--workers`) utilizing `concurrent.futures` and `tenacity` exponential backoff limiting. VectorEngine assigned as Priority 1 for transcription. (See `references/batch_processing.md` for technical design details).
