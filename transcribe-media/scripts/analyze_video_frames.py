
import os
import sys
import argparse
import base64
import subprocess
import tempfile
import glob
import shutil
import json
import requests
from pathlib import Path

# Configuration
# Default key from user's env/previous context
DEFAULT_KIE_KEY = "ba771c2577842b861f5e0fde91712af7" 
KIE_API_KEY = os.getenv("KIE_API_KEY", DEFAULT_KIE_KEY)
BASE_URL = "https://api.kie.ai/gemini-3-flash/v1/chat/completions"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_frames(video_path, output_dir, interval=10):
    """
    Extracts frames from the video every `interval` seconds.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"DEBUG: Extracting frames from {video_path} every {interval}s...")
    
    # ffmpeg command: extract one frame every X seconds
    # fps=1/10 means 1 frame every 10 seconds
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", f"fps=1/{interval},scale=320:-1", # Scale to 320px width to save tokens
        "-q:v", "7", # Quality 7 (more compression)
        f"{output_dir}/frame_%03d.jpg"
    ]
    
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        frames = sorted(glob.glob(f"{output_dir}/*.jpg"))
        print(f"DEBUG: Extracted {len(frames)} frames.")
        return frames
    except Exception as e:
        print(f"Error extracting frames: {e}")
        return []

def analyze_frames(frames, prompt):
    """
    Sends frames to Kie.ai Gemini.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {KIE_API_KEY}"
    }

    # Prepare Multimodal Content
    content = [{"type": "text", "text": prompt}]
    
    # Limit to max frames to avoid payload limits (e.g., 5 frames)
    # If more, we might need to sub-sample
    MAX_FRAMES = 5
    if len(frames) > MAX_FRAMES:
        step = len(frames) // MAX_FRAMES
        frames = frames[::step][:MAX_FRAMES]
        print(f"DEBUG: Subsampled to {len(frames)} frames for API payload.")

    for frame_path in frames:
        b64_data = encode_image(frame_path)
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64_data}"}
        })
        
    messages = [{"role": "user", "content": content}]
    
    payload = {
        "model": "gemini-3-flash", 
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 4096,
        "stream": False
    }
    
    print("DEBUG: Sending request to Kie.ai...")
    
    try:
        response = requests.post(BASE_URL, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            res_json = response.json()
            if "choices" in res_json and len(res_json["choices"]) > 0:
                return res_json["choices"][0]["message"]["content"]
            else:
                return f"Error: Unexpected response: {res_json}"
        else:
            return f"Error: API status {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Exception: {e}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Path to video file")
    parser.add_argument("--prompt", required=True, help="Analysis prompt")
    args = parser.parse_args()
    
    # Create temp dir for frames
    with tempfile.TemporaryDirectory() as temp_dir:
        frames = extract_frames(args.file, temp_dir, interval=15) # Every 15 seconds
        if not frames:
            print("Failed to extract frames.")
            return
            
        result = analyze_frames(frames, args.prompt)
        print("\n--- Analysis Result ---\n")
        print(result)

if __name__ == "__main__":
    main()
