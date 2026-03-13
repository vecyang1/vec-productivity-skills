---
name: youtube-downloader
description: Download YouTube videos with customizable quality and format options. Use this skill when the user asks to download, save, or grab YouTube videos. Supports various quality settings (best, 1080p, 720p, 480p, 360p), multiple formats (mp4, webm, mkv), and audio-only downloads as MP3.
---

# YouTube Video Downloader

Download YouTube videos with full control over quality and format settings.

## Quick Start

The simplest way to download a video:

```bash
python scripts/download_video.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

This downloads the video in best available quality as MP4 to `/mnt/user-data/outputs/`.

## Options

### Quality Settings

Use `-q` or `--quality` to specify video quality:

- `best` (default): Highest quality available
- `1080p`: Full HD
- `720p`: HD
- `480p`: Standard definition
- `360p`: Lower quality
- `worst`: Lowest quality available

Example:
```bash
python scripts/download_video.py "URL" -q 720p
```

### Format Options

Use `-f` or `--format` to specify output format (video downloads only):

- `mp4` (default): Most compatible
- `webm`: Modern format
- `mkv`: Matroska container

Example:
```bash
python scripts/download_video.py "URL" -f webm
```

### Audio Only

Use `-a` or `--audio-only` to download only audio as MP3:

```bash
python scripts/download_video.py "URL" -a
```

### Custom Output Directory

Use `-o` or `--output` to specify a different output directory:

```bash
python scripts/download_video.py "URL" -o /path/to/directory
```

## Batch Downloading

To download multiple videos in parallel, use the batch downloader with a CSV file or a direct playlist/channel URL:

```bash
# From a CSV file (must have a video_id column)
python scripts/batch_download.py --csv /path/to/videos.csv -o /mnt/user-data/outputs -w 5

# Directly from a playlist or channel URL
python scripts/batch_download.py --url "https://www.youtube.com/@some_channel/videos" -o /mnt/user-data/outputs -w 5
```

Options for batch downloading:
- `-o` / `--output`: Output directory
- `-w` / `--workers`: Number of parallel downloads (defaults to 5)
- `-a` / `--audio-only`: Download only audio as MP3

## Complete Examples

1. Download video in 1080p as MP4:
```bash
python scripts/download_video.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -q 1080p
```

2. Download audio only as MP3:
```bash
python scripts/download_video.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -a
```

3. Download in 720p as WebM to custom directory:
```bash
python scripts/download_video.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -q 720p -f webm -o /custom/path
```

## How It Works

The skill uses `yt-dlp`, a robust YouTube downloader that:
- Automatically installs itself if not present
- Fetches video information before downloading
- Selects the best available streams matching your criteria
- Merges video and audio streams when needed
- Supports a wide range of YouTube video formats

## Important Notes

- Downloads are saved to `/mnt/user-data/outputs/` by default
- Video filename is automatically generated from the video title
- The script handles installation of yt-dlp automatically
- Only single videos are downloaded (playlists are skipped by default)
- Higher quality videos may take longer to download and use more disk space

## Handling Large Audio for NotebookLM and Gemini

When transcribing massive amounts of audio (e.g., merging hundreds of videos) using Gemini or NotebookLM, you must respect the model's **1M Token Context Window limit**.

**The Token Mathematics:**
- Gemini's audio tokenization uses approximately **32 tokens per second** of audio.
- 1,000,000 tokens / 32 tokens/sec = 31,250 seconds 
- 31,250 seconds = **~8.6 Hours**

**Maximum Safe Limit:**
To leave enough room (~300k tokens) for system prompts and the generated transcribed text without crashing the context window, you should **never upload an audio file longer than 6 Hours** to Gemini 1.5 Pro/Flash.

**The Solution:**
This skill includes a `chunk_mp3s_by_duration.py` script specifically designed to solve this issue. It uses `ffprobe` to accurately calculate the duration of a folder of MP3s and concatenate them into perfectly sized chunks that will never exceed 6 hours.

```bash
# Combine a directory of MP3s into chunked files safe for NotebookLM
python scripts/chunk_mp3s_by_duration.py
```

## Troubleshooting

### HTTP Error 403: Forbidden
If you encounter a "HTTP Error 403: Forbidden" from YouTube, it likely means YouTube is blocking the default web client. 

**Solution:** Use the Android client emulation.

Add this flag to your `yt-dlp` command (if running raw) or rely on updated scripts that incorporate checks:
```bash
--extractor-args "youtube:player_client=android"
```
Or specifically for the Python script if you are modifying it:
```python
ydl_opts = {
    'extractor_args': {'youtube': {'player_client': ['android']}}
}
```

*Note: This workaround was verified working as of Jan 2026.*