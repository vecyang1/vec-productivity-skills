#!/usr/bin/env python3
"""
YouTube Channel Video Scraper
Extracts all video metadata from a YouTube channel.
"""

import argparse
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import re

def check_dependencies():
    """Check if yt-dlp or youtube-dl is installed."""
    # Try yt-dlp as command
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
        return ('yt-dlp', 'yt-dlp')
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Try yt-dlp as Python module
    try:
        subprocess.run(['python3', '-m', 'yt_dlp', '--version'], capture_output=True, check=True)
        return ('python3 -m yt_dlp', ['python3', '-m', 'yt_dlp'])
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Try youtube-dl
    try:
        subprocess.run(['youtube-dl', '--version'], capture_output=True, check=True)
        return ('youtube-dl', 'youtube-dl')
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    print("Error: Neither yt-dlp nor youtube-dl is installed.", file=sys.stderr)
    print("Install with: pip3 install yt-dlp", file=sys.stderr)
    sys.exit(1)

def parse_duration(duration_str):
    """Convert duration string to HH:MM:SS format."""
    if not duration_str:
        return "00:00:00"

    # Handle ISO 8601 duration format (PT1H2M3S)
    if duration_str.startswith('PT'):
        hours = re.search(r'(\d+)H', duration_str)
        minutes = re.search(r'(\d+)M', duration_str)
        seconds = re.search(r'(\d+)S', duration_str)

        h = int(hours.group(1)) if hours else 0
        m = int(minutes.group(1)) if minutes else 0
        s = int(seconds.group(1)) if seconds else 0

        return f"{h:02d}:{m:02d}:{s:02d}"

    return str(duration_str)

import csv

def scrape_channel(url, output_path, limit=None, downloader_info=None):
    """
    Scrape video metadata from a YouTube channel (metadata only, no downloads).

    Args:
        url: Channel URL
        output_path: Path where the final output will be saved (used for intermediate files)
        limit: Maximum number of videos to scrape (None for all)
        downloader_info: Tuple of (name, command) from check_dependencies()

    Returns:
        List of video metadata dictionaries
    """
    downloader_name, downloader_cmd = downloader_info
    print(f"Scraping channel: {url}", file=sys.stderr)
    print(f"Using: {downloader_name}", file=sys.stderr)

    # Build command - get all metadata in one go
    if isinstance(downloader_cmd, list):
        cmd = downloader_cmd.copy()
    else:
        cmd = [downloader_cmd]

    cmd.extend([
        '--dump-json',
        '--skip-download',
        '--no-warnings',
        '--ignore-errors',
        '--flat-playlist', # Huge speedup, doesn't load full individual pages
        url
    ])

    if limit:
        cmd.extend(['--playlist-end', str(limit)])

    print(f"Running: {' '.join(cmd)}", file=sys.stderr)
    print("Fetching metadata (streaming to disk)...", file=sys.stderr)
    
    # Setup intermediate output file in the same directory as final output
    out_dir = Path(output_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    intermediate_file = out_dir / "scraping_progress.jsonl"
    
    videos = []
    
    # CSV headers
    csv_headers = [
        'video_id', 'title', 'url', 'views', 'duration', 
        'published_date', 'published_relative', 'thumbnail', 'description'
    ]

    # Execute command using Popen to stream stdout
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        
        # Open both jsonl and csv files to stream to disk simultaneously
        with open(intermediate_file, 'w', encoding='utf-8') as prog_file, \
             open(output_path, 'w', newline='', encoding='utf-8-sig') as csv_file:
             
            writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
            if output_path.endswith('.csv'):
                writer.writeheader()
                
            i = 0
            for line in process.stdout:
                line = line.strip()
                if not line:
                    continue
                
                i += 1
                try:
                    video_data = json.loads(line)
        
                    # Extract video ID
                    video_id = video_data.get('id', '')
                    if not video_id:
                        continue
                        
                    full_title = video_data.get('title', '')
        
                    print(f"Processing {i}: {video_id} - {full_title}", file=sys.stderr)
        
                    # Extract relevant fields. With flat-playlist some fields might be under different names or missing
                    duration_val = video_data.get('duration_string', '') or video_data.get('duration', '')
                    
                    video_info = {
                        'video_id': video_id,
                        'title': full_title,
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'views': int(video_data.get('view_count') or 0),
                        'duration': parse_duration(str(duration_val)) if duration_val else '',
                        'published_date': video_data.get('upload_date', ''),
                        'published_relative': '',
                        'thumbnail': video_data.get('thumbnail', '') or video_data.get('thumbnails', [{'url': ''}])[0].get('url', ''),
                        'description': video_data.get('description', '')[:200] + '...' if video_data.get('description') else ''
                    }
        
                    # Format upload date
                    if video_info['published_date']:
                        try:
                            date_obj = datetime.strptime(video_info['published_date'], '%Y%m%d')
                            video_info['published_date'] = date_obj.strftime('%Y-%m-%d')
        
                            # Calculate relative time
                            days_ago = (datetime.now() - date_obj).days
                            if days_ago == 0:
                                video_info['published_relative'] = 'Today'
                            elif days_ago == 1:
                                video_info['published_relative'] = '1 day ago'
                            elif days_ago < 30:
                                video_info['published_relative'] = f'{days_ago} days ago'
                            elif days_ago < 365:
                                months = days_ago // 30
                                video_info['published_relative'] = f'{months} month{"s" if months > 1 else ""} ago'
                            else:
                                years = days_ago // 365
                                video_info['published_relative'] = f'{years} year{"s" if years > 1 else ""} ago'
                        except ValueError:
                            pass
        
                    videos.append(video_info)
                    
                    # Write to intermediate JSONL file continuously
                    prog_file.write(json.dumps(video_info, ensure_ascii=False) + '\n')
                    prog_file.flush()
                    
                    # Write to CSV file continuously
                    if output_path.endswith('.csv'):
                        writer.writerow(video_info)
                        csv_file.flush()
        
                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse line {i}: {e}", file=sys.stderr)
                    continue
                    
        # Wait for process to finish
        process.wait()
        
        if process.returncode != 0 and len(videos) == 0:
            stderr_output = process.stderr.read()
            print(f"Error running {downloader_name}: exited with {process.returncode}", file=sys.stderr)
            print(f"stderr: {stderr_output}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error running {downloader_name}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(videos)} videos", file=sys.stderr)
    return videos

def save_csv(videos, output_path):
    """Save videos to CSV file."""
    try:
        import pandas as pd
    except ImportError:
        print("Error: pandas is required for CSV output", file=sys.stderr)
        print("Install with: pip3 install pandas", file=sys.stderr)
        sys.exit(1)

    df = pd.DataFrame(videos)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Saved {len(videos)} videos to {output_path}", file=sys.stderr)

def save_json(videos, output_path):
    """Save videos to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(videos)} videos to {output_path}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(
        description='Scrape video metadata from a YouTube channel',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape all videos to CSV
  %(prog)s --url "https://www.youtube.com/@ZJSTV-Music/videos" --output data.csv

  # Scrape first 100 videos to JSON
  %(prog)s --url "https://www.youtube.com/@ZJSTV-Music/videos" --limit 100 --format json --output data.json
        """
    )

    parser.add_argument('--url', required=True, help='YouTube channel URL')
    parser.add_argument('--output', '-o', required=True, help='Output file path')
    parser.add_argument('--limit', type=int, help='Maximum number of videos to scrape')
    parser.add_argument('--format', choices=['csv', 'json'], default='csv', help='Output format (default: csv)')

    args = parser.parse_args()

    # Check dependencies
    downloader_info = check_dependencies()

    # Scrape channel
    videos = scrape_channel(args.url, args.output, args.limit, downloader_info)

    if not videos:
        print("No videos found", file=sys.stderr)
        sys.exit(1)

    # Note: JSON saves if requested, otherwise CSV was already saved during stream
    if args.format != 'csv':
        save_json(videos, args.output)

    print(f"\nSummary:", file=sys.stderr)
    print(f"  Total videos: {len(videos)}", file=sys.stderr)
    print(f"  Total views: {sum(int(v.get('views') or 0) for v in videos):,}", file=sys.stderr)
    print(f"  Output: {args.output}", file=sys.stderr)

if __name__ == '__main__':
    main()
