import os
import sys
import argparse
import requests
import json
import base64
import subprocess
import tempfile
from pathlib import Path

# Configuration
from dotenv import load_dotenv
import model_config
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

config = model_config.get_provider_config()
GOOGLE_API_KEY = config["api_key"] if config else None
GOOGLE_MODEL = config["model"] if config else "gemini-3.1-flash-lite-preview"
BASE_URL = f"{config['base_url'] if config else 'https://generativelanguage.googleapis.com/v1beta'}/models/{GOOGLE_MODEL}:generateContent"
MAX_VIDEO_SIZE_MB = 25  # Compress if larger than this

def compress_video(input_path):
    """
    Compresses video to a temporary file using ffmpeg.
    Target: 720p, 20fps, CRF 28 (Optimized for LLM vision & upload speed).
    """
    try:
        # User requested ALL videos be compressed for speed/efficiency
        # file_size_mb = os.path.getsize(input_path) / (1024 * 1024)
        print(f"DEBUG: Optimizing video for LLM (720p, 20fps)...")
        
        temp_fd, temp_path = tempfile.mkstemp(suffix=".mp4")
        os.close(temp_fd)
        
        # ffmpeg command: scale to 720p height (preserve aspect), 20fps (enough for context), crf 28 (lower quality)
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-vf", "scale=-2:720,fps=20", 
            "-c:v", "libx264", "-crf", "28", "-preset", "faster",
            "-c:a", "aac", "-b:a", "64k", # Minimize audio size
            temp_path
        ]
        
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        new_size = os.path.getsize(temp_path) / (1024 * 1024)
        print(f"DEBUG: Compressed to {new_size:.2f}MB")
        
        return temp_path, True
    except Exception as e:
        print(f"Warning: Compression failed ({e}). Using original file.")
        return input_path, False

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

class RateLimitException(Exception):
    pass

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60), 
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type((requests.exceptions.RequestException, RateLimitException))
)
def transcribe_google(prompt, media_path=None, media_type="audio", temperature=0.0):
    """
    Interacts with Google Gemini API via REST (generateContent) with exponential backoff.
    """
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not found.")
        return False

    url = f"{BASE_URL}?key={GOOGLE_API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }

    parts = []
    
    # helper for mime types
    import mimetypes
    
    is_temp = False
    if media_path:
        # Check media type logic
        if "video" in media_type or any(media_path.lower().endswith(ext) for ext in ['.mp4', '.mov', '.avi', '.webm']):
             media_type = "video"
             # Compression
             if not media_path.startswith("http"):
                 media_path, is_temp = compress_video(media_path)

        # Check if URL or local file
        is_url = media_path.startswith("http")
        
        # YouTube check
        youtube_patterns = ['youtube.com/watch', 'youtu.be/', 'youtube.com/shorts/', 'youtube.com/embed/']
        is_youtube = is_url and any(pattern in media_path for pattern in youtube_patterns)
        
        try:
            if is_youtube:
                print(f"DEBUG: Detected YouTube URL {media_path}. Passing directly to Gemini via fileUri...")
                parts.append({
                    "fileData": {
                        "fileUri": media_path,
                        "mimeType": "video/mp4"
                    }
                })
            else:
                if is_url:
                    # For Google API, download URL to temp
                    print("DEBUG: Downloading media from URL...")
                    response = requests.get(media_path)
                    response.raise_for_status()
                    with tempfile.NamedTemporaryFile(delete=False) as f:
                        f.write(response.content)
                        media_path = f.name
                        is_temp = True

                # Local File Processing
                mime_type, _ = mimetypes.guess_type(media_path)
                if not mime_type:
                    if media_type == "video": mime_type = "video/mp4"
                    elif media_type == "audio": mime_type = "audio/mp3"
                    else: mime_type = "image/jpeg"
                
                print(f"DEBUG: Encoded local file with mime-type: {mime_type}")
                b64_data = encode_image(media_path)
                
                parts.append({
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": b64_data
                    }
                })
                    
        except Exception as e:
            print(f"Error processing media: {e}")
            return False
            
        finally:
            # Cleanup temp file if compressed or downloaded
            if is_temp and os.path.exists(media_path):
                os.remove(media_path)
                print("DEBUG: Cleaned up temp file.")
            
    # Add text prompt (always valid)
    parts.append({"text": prompt})

    payload = {
        "contents": [{
            "parts": parts
        }],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 8192
        }
    }

    try:
        if os.getenv("DEBUG"):
            print(f"DEBUG: Posting to Google API...")
        
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 429 or response.status_code >= 500:
            print(f"DEBUG: Rate limit or Server Error ({response.status_code}). Retrying...")
            raise RateLimitException(f"API Error {response.status_code}")
            
        response.raise_for_status()
        
        try:
            res_json = response.json()
            if "candidates" in res_json and len(res_json["candidates"]) > 0:
                content_parts = res_json["candidates"][0]["content"]["parts"]
                text_response = "".join([p.get("text", "") for p in content_parts])
                return text_response
            else:
                print("Error: Unexpected response format.")
                print(json.dumps(res_json, indent=2))
                return False
        except json.JSONDecodeError:
            print("Error: Failed to decode JSON response.")
            return False

    except Exception as e:
        if isinstance(e, RateLimitException):
            raise e
        print(f"Exception: {e}")
        return False

def process_single_file(prompt, file_path, media_type, out_dir):
    """Process a single file, save output, and skip if already processed."""
    base_name = os.path.basename(file_path)
    
    # Check if passing a pure URL via `-f https://youtube.com/...`
    if file_path.startswith("http"):
        import urllib.parse
        parsed = urllib.parse.urlparse(file_path)
        # Use query/path chars or 'youtube_url' to name the local txt
        base_name = os.path.basename(parsed.path) or "url"
        if 'youtube' in file_path or 'youtu.be' in file_path:
            base_name = "youtube_video"
            
    filename_without_ext = os.path.splitext(base_name)[0]
    
    out_path = os.path.join(out_dir, f"{filename_without_ext}_transcript.txt")
    
    if os.path.exists(out_path):
        print(f"Skipping {base_name}: Transcript already exists at {out_path}")
        return True
        
    print(f"Processing {base_name}...")
    try:
        result = transcribe_google(prompt, file_path, media_type)
        if result:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"Success: {base_name} -> {out_path}")
            return True
        else:
            print(f"Failed to transcribe: {base_name}")
            return False
    except Exception as e:
         print(f"Failed to transcribe {base_name} after retries: {e}")
         return False

def main():
    parser = argparse.ArgumentParser(description="Gemini 3.1 Flash Lite - Transcribe Media")
    parser.add_argument("prompt", help="Text prompt")
    parser.add_argument("--file", "-f", help="Path or URL to single image/video/audio file")
    parser.add_argument("--dir", help="Directory containing multiple media files to batch process")
    parser.add_argument("--out-dir", help="Directory to save output TXT files (defaults to same dir as input)")
    parser.add_argument("--workers", type=int, default=5, help="Number of parallel workers for batch processing (default: 5)")
    parser.add_argument("--type", "-t", default="image", choices=["image", "video", "audio"], help="Media type (used for validation logic)")
    parser.add_argument("--key", help="API Key (optional, defaults to env/hardcoded)")
    
    args = parser.parse_args()
    
    global GOOGLE_API_KEY
    if args.key:
        GOOGLE_API_KEY = args.key
        
    if not args.file and not args.dir:
         print("Error: Either --file or --dir must be provided.")
         sys.exit(1)
         
    if args.dir:
        input_dir = args.dir
        if not os.path.isdir(input_dir):
            print(f"Error: Directory {input_dir} not found.")
            sys.exit(1)
            
        out_dir = args.out_dir if args.out_dir else input_dir
        os.makedirs(out_dir, exist_ok=True)
        
        # Support common extensions 
        extensions = ['.mp3', '.wav', '.m4a', '.mp4', '.mov', '.avi', '.webm']
        files_to_process = [
            os.path.join(input_dir, f) for f in os.listdir(input_dir)
            if any(f.lower().endswith(ext) for ext in extensions)
        ]
        
        if not files_to_process:
            print(f"No valid media files found in {input_dir}")
            sys.exit(0)
            
        print(f"Found {len(files_to_process)} files to process. Starting batch with {args.workers} workers...")
        
        success_count = 0
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {executor.submit(process_single_file, args.prompt, fp, args.type, out_dir): fp for fp in files_to_process}
            for future in as_completed(futures):
                if future.result():
                    success_count += 1
                    
        print(f"Batch processing complete. Successfully processed: {success_count}/{len(files_to_process)}")

    else:
        # Single file
        out_dir = args.out_dir if args.out_dir else os.path.dirname(os.path.abspath(args.file))
        os.makedirs(out_dir, exist_ok=True)
        res = process_single_file(args.prompt, args.file, args.type, out_dir)
        if res and not args.out_dir:
             print("Single file processed successfully.")

if __name__ == "__main__":
    main()
