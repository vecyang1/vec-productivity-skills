#!/usr/bin/env python3
"""
Audio Optimizer for NotebookLM / Gemini
Compresses MP3s down to 32kbps Mono to drastically reduce file size for LLM transcription (usually 1/10th the size) without losing speech intelligibility.
"""

import os
import glob
import subprocess
import concurrent.futures
import sys
import argparse

def optimize_file(input_file, output_file):
    """Compress audio to 32kbps mono using ffmpeg."""
    # -ac 1 = Mono audio (speech doesn't need stereo)
    # -ar 24000 = Sample rate (plenty for voice)
    # -b:a 32k = 32 kbps bitrate (extremely small, perfectly intelligible for LLMs)
    cmd = [
        "ffmpeg", "-y", "-i", input_file,
        "-ac", "1", "-ar", "24000", "-b:a", "32k",
        "-loglevel", "error",
        output_file
    ]
    try:
        subprocess.run(cmd, check=True)
        return (True, input_file, output_file)
    except subprocess.CalledProcessError as e:
        return (False, input_file, str(e))

def main():
    parser = argparse.ArgumentParser(description="Shrink MP3s for NotebookLM upload (32kbps Mono)")
    parser.add_argument("-d", "--dir", default=".", help="Directory containing the MP3s")
    parser.add_argument("-w", "--workers", type=int, default=4, help="Number of parallel compressions")
    args = parser.parse_args()

    input_dir = args.dir
    output_dir = os.path.join(input_dir, "optimized_for_llm")
    
    mp3_files = glob.glob(os.path.join(input_dir, "*.mp3"))
    
    # Don't try to compress files that are already compressed
    mp3_files = [f for f in mp3_files if "optimized_for_llm" not in f]

    if not mp3_files:
        print(f"No MP3 files found in {input_dir}.")
        sys.exit(0)

    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Found {len(mp3_files)} MP3s. Compressing to 32kbps Mono for NotebookLM...")
    print(f"Target directory: {output_dir}")
    print(f"Using {args.workers} parallel workers. This may take a while.\n")

    total_original_size = 0
    total_new_size = 0
    success_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {}
        for mp3 in mp3_files:
            original_size = os.path.getsize(mp3)
            total_original_size += original_size
            
            basename = os.path.basename(mp3)
            out_file = os.path.join(output_dir, basename.replace(".mp3", "_compressed.mp3"))
            
            futures[executor.submit(optimize_file, mp3, out_file)] = (mp3, out_file)

        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            success, in_f, result = future.result()
            basename = os.path.basename(in_f)
            
            if success:
                new_size = os.path.getsize(result)
                total_new_size += new_size
                success_count += 1
                ratio = (1 - (new_size / os.path.getsize(in_f))) * 100
                print(f"[{i}/{len(mp3_files)}] ✅ Compressed {basename} (Saved {ratio:.1f}%)")
            else:
                print(f"[{i}/{len(mp3_files)}] ❌ Failed {basename}: {result}")

    orig_mb = total_original_size / (1024 * 1024)
    new_mb = total_new_size / (1024 * 1024)
    
    print("\n" + "="*40)
    print("COMPRESSION COMPLETE")
    print("="*40)
    print(f"Original Size: {orig_mb:.1f} MB")
    print(f"New Size:      {new_mb:.1f} MB")
    if orig_mb > 0:
        print(f"Total Reduced: {(1 - (new_mb/orig_mb))*100:.1f}%")
    print(f"Files Saved at: {output_dir}")

if __name__ == '__main__':
    main()
