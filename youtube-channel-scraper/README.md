# YouTube Channel Scraper

Created: 2026-03-02
Author: Vee
Version: 1.0.0

## Purpose

Scrape all video metadata from any YouTube channel including titles, views (播放量), duration, and publish dates. No downloads required - metadata only.

## Usage

```bash
# Scrape all videos from a channel
python3 ~/.claude/skills/youtube-channel-scraper/scripts/scrape_channel.py \
  --url "https://www.youtube.com/@ZJSTV-Music/videos" \
  --output channel_data.csv

# Limit to recent videos
python3 ~/.claude/skills/youtube-channel-scraper/scripts/scrape_channel.py \
  --url "https://www.youtube.com/@ZJSTV-Music/videos" \
  --limit 100 \
  --output recent_videos.csv

# JSON output
python3 ~/.claude/skills/youtube-channel-scraper/scripts/scrape_channel.py \
  --url "https://www.youtube.com/@ZJSTV-Music/videos" \
  --format json \
  --output channel_data.json
```

## Output Fields

- `video_id`: YouTube video ID
- `title`: Video title (标题)
- `url`: Full video URL
- `views`: View count (播放量)
- `duration`: Video duration (HH:MM:SS)
- `published_date`: Upload date (YYYY-MM-DD)
- `published_relative`: Relative time (e.g., "2 days ago")
- `thumbnail`: Thumbnail URL
- `description`: Video description (first 200 chars)

## Dependencies

- yt-dlp (installed via pip3)
- pandas (for CSV output)

## Example Output

```csv
video_id,title,url,views,duration,published_date,published_relative
lHBuTqNdt8o,【歌荒必听】2月霸榜热曲推荐！...,https://...,963,1:29:31,2026-03-01,1 day ago
```

## Notes

- Fast: metadata-only extraction, no video downloads
- Efficient: single API call per channel
- Reliable: uses yt-dlp (most up-to-date YouTube scraper)
- No API key required
- **Important**: For channels with many videos, use `--limit` to avoid long wait times
- Tested: Successfully scraped 100 videos from ZJSTV-Music channel (2026-03-02)

## Recent Usage

```bash
# ZJSTV-Music channel - 100 videos scraped
python3 ~/.claude/skills/youtube-channel-scraper/scripts/scrape_channel.py \
  --url "https://www.youtube.com/@ZJSTV-Music/videos" \
  --limit 100 \
  --output "zjstv_videos.csv"
# Result: 100 videos, 267 CSV lines, titles in Chinese preserved
```
