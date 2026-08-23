#!/usr/bin/env python3
"""
YouTube Batch Video Downloader
Downloads multiple videos in parallel from a CSV file or playlist.
"""

import argparse
import sys
import subprocess
import csv
import os
import concurrent.futures
from pathlib import Path

def download_single(video_id, url, output_path, audio_only=False, max_retries=3):
    """Download a single video with yt-dlp."""
    cmd = [
        "python3", "-m", "yt_dlp",
        "--ignore-errors",
        "--no-warnings",
        "--no-playlist",
        "--extractor-args", "youtube:player_client=android",
        "--retries", str(max_retries)
    ]
    
    if audio_only:
        cmd.extend([
            "-x", "--audio-format", "mp3", "--audio-quality", "3"
        ])
    else:
        cmd.extend([
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4"
        ])
        
    cmd.extend([
        "--download-archive", os.path.join(output_path, "download_archive.txt"),
        "-o", os.path.join(output_path, "%(upload_date)s - %(title)s.%(ext)s"),
        url
    ])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            if "has already been recorded in the archive" in result.stdout or "has already been downloaded" in result.stdout:
                return (video_id, "Skipped (Already downloaded)")
            return (video_id, "Success")
        else:
            return (video_id, f"Error (Exit {result.returncode})")
    except Exception as e:
        return (video_id, f"Failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Batch download YouTube videos in parallel")
    parser.add_argument("--csv", help="Path to CSV file containing video_id column")
    parser.add_argument("--url", help="URL of a YouTube playlist or channel to batch download")
    parser.add_argument("-o", "--output", default="/mnt/user-data/outputs", help="Output directory")
    parser.add_argument("-a", "--audio-only", action="store_true", help="Download audio only as MP3")
    parser.add_argument("-w", "--workers", type=int, default=5, help="Number of parallel downloads (default 5)")
    args = parser.parse_args()

    if not args.csv and not args.url:
        print("Error: Must provide either --csv or --url", file=sys.stderr)
        sys.exit(1)

    Path(args.output).mkdir(parents=True, exist_ok=True)
    videos = []

    if args.csv:
        print(f"Reading videos from CSV: {args.csv}")
        with open(args.csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                v_id = row.get('video_id')
                if v_id:
                    videos.append((v_id, f"https://www.youtube.com/watch?v={v_id}"))
    elif args.url:
        print(f"Fetching playlist/channel metadata from: {args.url}")
        # Fetch playlist using yt-dlp flat-playlist
        cmd = [
            "python3", "-m", "yt_dlp", "--dump-json", "--flat-playlist", 
            "--ignore-errors", "--no-warnings", args.url
        ]
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
            for line in process.stdout:
                line = line.strip()
                if not line: continue
                import json
                try:
                    data = json.loads(line)
                    v_id = data.get('id')
                    if v_id:
                        videos.append((v_id, f"https://www.youtube.com/watch?v={v_id}"))
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"Failed to fetch playlist: {e}")
            sys.exit(1)

    total = len(videos)
    if total == 0:
        print("No videos found to download.")
        sys.exit(0)

    print(f"Found {total} videos. Starting parallel download with {args.workers} workers...")
    
    success_count = 0
    skip_count = 0
    error_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(download_single, v_id, url, args.output, args.audio_only): v_id for v_id, url in videos}
        for count, future in enumerate(concurrent.futures.as_completed(futures), 1):
            v_id = futures[future]
            try:
                vid, status = future.result()
                print(f"[{count}/{total}] {vid}: {status}", flush=True)
                if status == "Success":
                    success_count += 1
                elif "Skipped" in status:
                    skip_count += 1
                else:
                    error_count += 1
            except Exception as exc:
                print(f"[{count}/{total}] {v_id}: Exception generated -> {exc}", flush=True)
                error_count += 1

    print("\n--- Download Summary ---")
    print(f"Total processed: {total}")
    print(f"Success/New: {success_count}")
    print(f"Skipped (Already dl'd): {skip_count}")
    print(f"Errors: {error_count}")
    print(f"Output Directory: {args.output}")

if __name__ == '__main__':
    main()
