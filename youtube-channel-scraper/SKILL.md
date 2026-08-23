# YouTube Channel Scraper

Scrape all video metadata from a YouTube channel including titles, views, duration, and publish dates.

## Usage

```bash
# Scrape all videos from a channel
python3 ~/.claude/skills/youtube-channel-scraper/scripts/scrape_channel.py \
  --url "https://www.youtube.com/@ZJSTV-Music/videos" \
  --output channel_data.csv

# Limit number of videos
python3 ~/.claude/skills/youtube-channel-scraper/scripts/scrape_channel.py \
  --url "https://www.youtube.com/@ZJSTV-Music/videos" \
  --limit 100 \
  --output recent_videos.csv

# JSON output format
python3 ~/.claude/skills/youtube-channel-scraper/scripts/scrape_channel.py \
  --url "https://www.youtube.com/@ZJSTV-Music/videos" \
  --format json \
  --output channel_data.json
```

## Features

- Scrapes video title, views, duration, publish date
- Supports CSV and JSON output formats
- Handles pagination for channels with many videos
- Rate limiting to avoid being blocked
- Progress tracking for large channels

## Output Fields

- `video_id`: YouTube video ID
- `title`: Video title
- `url`: Full video URL
- `views`: View count (播放量)
- `duration`: Video duration (HH:MM:SS)
- `published_date`: Upload date (YYYY-MM-DD)
- `published_relative`: Relative time (e.g., "2 days ago")
- `thumbnail`: Thumbnail URL

## Dependencies

- yt-dlp (recommended) or youtube-dl
- pandas (for CSV output)

## Installation

```bash
pip3 install yt-dlp pandas
```

## Notes

- Uses yt-dlp for reliable metadata extraction
- No API key required (scrapes public data)
- Respects YouTube's rate limits
- For very large channels (1000+ videos), consider using --limit
- **Performance**: ~100 videos takes ~2-3 minutes, full channel scrape may take 10-30+ minutes depending on size
- **Directory requirement**: Output directory must exist before running (script will fail otherwise)

## Troubleshooting

- **Error: "Cannot save file into a non-existent directory"**: Create the output directory first with `mkdir -p /path/to/directory`
- **Slow scraping**: Large channels take time. Use `--limit` for faster results or run in background with `&`
- **yt-dlp not found**: The script auto-detects `yt-dlp` command or `python3 -m yt_dlp` module
