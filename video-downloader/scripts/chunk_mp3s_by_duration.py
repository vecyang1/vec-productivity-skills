import os
import glob
import subprocess
import sys

# 1M tokens in Gemini 1.5 is roughly 8.6 hours of audio (32 tokens per second).
# We set a safe limit of 6 hours (21600 seconds) to leave ~300k tokens for prompts and text.
MAX_CHUNK_DURATION = 21600 

folder = "/Volumes/disk_y/Cowork-SSD/Mike working folder"

def get_duration(file_path):
    """Get the duration of a video/audio file in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of",
        "default=noprint_wrappers=1:nokey=1", file_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Warning: Failed to read duration for {file_path} - {e}")
        return 0.0

print("Scanning for previously created chunks to remove...")
old_chunks = glob.glob(os.path.join(folder, "mike1111_chunk_*.mp3"))
for oc in old_chunks:
    os.remove(oc)

mp3_files = sorted(glob.glob(os.path.join(folder, "*.mp3")))

if not mp3_files:
    print("No MP3 files found.")
    sys.exit(1)

print(f"Found {len(mp3_files)} MP3 files. Calculating durations (this might take a moment)...")

chunks = []
current_chunk = []
current_duration = 0.0

for mp3 in mp3_files:
    dur = get_duration(mp3)
    # If a single file exceeds the duration, it gets its own chunk to prevent infinite loop.
    if current_duration + dur > MAX_CHUNK_DURATION and current_chunk:
        chunks.append(current_chunk)
        current_chunk = [mp3]
        current_duration = dur
    else:
        current_chunk.append(mp3)
        current_duration += dur

if current_chunk:
    chunks.append(current_chunk)

print(f"\nNotebookLM Optimization: Splitting into {len(chunks)} chunked files (Safe 6-hour limit).")

for i, chunk_files in enumerate(chunks, 1):
    output_file = os.path.join(folder, f"mike1111_chunk_{i:03d}.mp3")
    concat_file = os.path.join(folder, f"concat_chunk_{i:03d}.txt")
    
    # Write the concat list for ffmpeg
    with open(concat_file, "w", encoding="utf-8") as f:
        for mp3 in chunk_files:
            safe_name = mp3.replace("'", "'\\''")
            f.write(f"file '{safe_name}'\n")
            
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", output_file]
    
    print(f"[{i}/{len(chunks)}] Combining {len(chunk_files)} files into {os.path.basename(output_file)}...")
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  -> Success: {os.path.basename(output_file)}")
    except subprocess.CalledProcessError as e:
        print(f"  -> ❌ Failed on chunk {i}. ffmpeg error: {e}")
    finally:
        if os.path.exists(concat_file):
            os.remove(concat_file)

print("\n✅ All chunking completed! These files are properly sized for the 1M token context window.")
