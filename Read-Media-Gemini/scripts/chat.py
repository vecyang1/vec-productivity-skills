import argparse
import base64
import logging
import mimetypes
import os
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from google import genai
from google.genai import types
from dotenv import load_dotenv
import openai

# Google Drive imports
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    import io
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False
    logging.warning("Google Drive dependencies not installed. Drive URLs will not work.")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Google Drive Configuration
GDRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def extract_drive_file_id(url_or_id):
    """Extract file ID from Google Drive URL or return as-is if already an ID."""
    if not url_or_id:
        return None

    # Pattern: https://drive.google.com/file/d/FILE_ID/view
    # Pattern: https://drive.google.com/open?id=FILE_ID
    patterns = [
        r'drive\.google\.com/file/d/([a-zA-Z0-9_-]+)',
        r'drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)',
        r'^([a-zA-Z0-9_-]{25,})$'  # Direct file ID
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    return None

def get_drive_credentials():
    """Get Google Drive credentials using gcloud or oauth_creds.json."""
    creds = None
    token_path = os.path.expanduser('~/.gdrive_token.json')
    oauth_creds_path = os.path.expanduser('~/oauth_creds.json')

    # Try loading existing token
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, GDRIVE_SCOPES)
        except Exception as e:
            logging.warning(f"Failed to load token: {e}")

    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            logging.warning(f"Failed to refresh token: {e}")
            creds = None

    # Try gcloud credentials
    if not creds or not creds.valid:
        try:
            result = subprocess.run(
                ['gcloud', 'auth', 'application-default', 'print-access-token'],
                capture_output=True,
                text=True,
                check=True
            )
            access_token = result.stdout.strip()
            if access_token:
                creds = Credentials(token=access_token)
                logging.info("Using gcloud credentials")
                return creds
        except Exception as e:
            logging.debug(f"gcloud not available: {e}")

    # Try OAuth flow with oauth_creds.json
    if not creds or not creds.valid:
        if os.path.exists(oauth_creds_path):
            try:
                flow = InstalledAppFlow.from_client_secrets_file(oauth_creds_path, GDRIVE_SCOPES)
                creds = flow.run_local_server(port=0)
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                logging.info("Created new OAuth credentials")
            except Exception as e:
                logging.error(f"OAuth flow failed: {e}")
                return None
        else:
            logging.error("No credentials found. Need gcloud or ~/oauth_creds.json")
            return None

    return creds

def download_from_drive(file_id):
    """Download a file from Google Drive and return the local path."""
    if not GDRIVE_AVAILABLE:
        logging.error("Google Drive dependencies not installed")
        return None

    try:
        creds = get_drive_credentials()
        if not creds:
            logging.error("Failed to get Drive credentials")
            return None

        service = build('drive', 'v3', credentials=creds)

        # Get file metadata
        file_metadata = service.files().get(fileId=file_id, fields='name,mimeType').execute()
        file_name = file_metadata.get('name', f'gdrive_{file_id}')
        mime_type = file_metadata.get('mimeType', '')

        logging.info(f"Downloading from Drive: {file_name} ({mime_type})")

        # Create temp file with proper extension
        _, ext = os.path.splitext(file_name)
        temp_fd, temp_path = tempfile.mkstemp(suffix=ext)
        os.close(temp_fd)

        # Download file
        request = service.files().get_media(fileId=file_id)
        with open(temp_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    logging.info(f"Download progress: {int(status.progress() * 100)}%")

        file_size_mb = os.path.getsize(temp_path) / (1024 * 1024)
        logging.info(f"Downloaded {file_name} ({file_size_mb:.2f}MB)")

        return temp_path

    except Exception as e:
        logging.error(f"Failed to download from Drive: {e}")
        return None

def is_drive_url(path):
    """Check if the path is a Google Drive URL."""
    if not path:
        return False
    return 'drive.google.com' in path or (len(path) >= 25 and re.match(r'^[a-zA-Z0-9_-]+$', path))

def is_youtube_url(path):
    """Check if the path is a YouTube URL."""
    if not path:
        return False
    youtube_patterns = [
        'youtube.com/watch',
        'youtu.be/',
        'youtube.com/shorts/',
        'youtube.com/embed/',
    ]
    return any(pattern in path for pattern in youtube_patterns)


import model_config

config = model_config.get_provider_config()

# Vector Engine (Primary)
VECTORENGINE_API_KEY = config["api_key"] if config and config["provider"] == "vectorengine" else None
VECTORENGINE_BASE_URL = config["base_url"] if config and config["provider"] == "vectorengine" else "https://api.vectorengine.ai"
VECTORENGINE_MODEL = config["model"] if config and config["provider"] == "vectorengine" else "gemini-3-flash-preview"

# Google Direct Fallback
GOOGLE_API_KEY = config["api_key"] if config and config["provider"] == "google" else os.getenv("GOOGLE_API_KEY", "")

# Antigravity Local Proxy Configuration
ANTIGRAVITY_API_KEY = os.getenv("ANTIGRAVITY_API_KEY", "")
ANTIGRAVITY_BASE_URL = os.getenv("ANTIGRAVITY_BASE_URL", "http://127.0.0.1:8045")

# Provider selection
PRIMARY_PROVIDER = config["provider"] if config else "vectorengine"

# Model Priority List (updated 2026-03-12)
MODEL_PRIORITY = [
    VECTORENGINE_MODEL,
    "gemini-3-flash-preview",  # Latest Flash model
    "gemini-2.5-flash",        # Fallback
]

def create_client_vectorengine(api_key, base_url):
    """Creates a google.genai Client using the Vector Engine proxy.
    NOTE: They provide OpenAI-compatible endpoints directly, but also
    support Google SDK passthrough on /v1beta/models/...
    """
    if not api_key:
        return None
    # Provide the root URL; the SDK appends /v1beta/models/...
    logging.info(f"Configuring GenAI with Vector Engine: {base_url}")
    return genai.Client(api_key=api_key, http_options={'base_url': base_url, 'api_version': 'v1beta'})

def create_client_proxy(api_key, base_url):
    """Creates a google.genai Client using the Antigravity local proxy."""
    if not api_key:
        return None
    logging.info(f"Configuring GenAI with proxy: {base_url}")
    return genai.Client(api_key=api_key, http_options={'base_url': base_url, 'api_version': 'v1beta'})

def create_client_google(api_key):
    """Creates a google.genai Client using Google Direct."""
    if not api_key:
        return None
    logging.info("Configuring GenAI with Google Direct")
    return genai.Client(api_key=api_key)

def generate_content_kie(prompt, media_paths, temperature=0.0, timeout=30):
    """Generate content via Kie AI (OpenAI-compatible). Images only — videos fall through."""
    if not KIE_API_KEY:
        return None
    # Skip video for Kie (no File API support)
    if media_paths and any(p.lower().endswith((".mp4", ".mov", ".avi", ".webm", ".mkv")) for p in (media_paths or [])):
        logging.info("Kie: skipping video, falling through to Google")
        return None

    content = [{"type": "text", "text": prompt}]
    for path in (media_paths or []):
        mime_type, _ = mimetypes.guess_type(path)
        mime_type = mime_type or "image/jpeg"
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        content.append({"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}})

    def _call():
        client = openai.OpenAI(api_key=KIE_API_KEY, base_url=KIE_BASE_URL)
        resp = client.chat.completions.create(
            model=KIE_MODEL,
            messages=[{"role": "user", "content": content}],
            temperature=temperature,
            stream=False,
        )
        return resp.choices[0].message.content

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(_call).result(timeout=timeout)
    except Exception as e:
        logging.error(f"Kie error: {e}")
        return None

def compress_video(input_path):
    """
    Compress a local video to a temporary file using ffmpeg.
    Target: 720p, 20fps, CRF 28 for faster upload and lower token/image cost.
    """
    try:
        logging.info("Optimizing video for LLM (720p, 20fps)...")
        temp_fd, temp_path = tempfile.mkstemp(suffix=".mp4")
        os.close(temp_fd)

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-vf",
            "scale=-2:720,fps=20",
            "-c:v",
            "libx264",
            "-crf",
            "28",
            "-preset",
            "faster",
            "-c:a",
            "aac",
            "-b:a",
            "64k",
            temp_path,
        ]
        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )

        new_size_mb = os.path.getsize(temp_path) / (1024 * 1024)
        logging.info(f"Compressed to {new_size_mb:.2f}MB")
        return temp_path, True
    except Exception as exc:
        logging.warning(f"Compression failed ({exc}). Using original file.")
        return input_path, False

def load_media_items(media_paths, media_type_hint="image", client=None, youtube_urls=None):
    """Loads media items for SDK usage. Inline bytes for images, File API for videos, direct URLs for YouTube."""
    items = []
    temp_files = []

    # Handle YouTube URLs first (pass directly to Gemini)
    if youtube_urls:
        for yt_url in youtube_urls:
            logging.info(f"Adding YouTube URL (direct): {yt_url}")
            try:
                items.append(types.Part.from_uri(file_uri=yt_url, mime_type="video/mp4"))
            except Exception as e:
                logging.error(f"Failed to add YouTube URL {yt_url}: {e}")

    if not media_paths:
        return items, temp_files

    if not isinstance(media_paths, list):
        media_paths = [media_paths]

    for path in media_paths:
        local_path = path
        is_temp = False
        lowered = path.lower()
        is_video = any(lowered.endswith(ext) for ext in [".mp4", ".mov", ".avi", ".webm", ".mkv"])

        if is_video:
             local_path, is_temp = compress_video(path)
             if is_temp:
                 temp_files.append(local_path)

        mime_type, _ = mimetypes.guess_type(local_path)

        if not is_video:
            logging.info(f"Loading image inline (SDK): {local_path}...")
            try:
                with open(local_path, "rb") as f:
                    data = f.read()
                items.append(types.Part.from_bytes(data=data, mime_type=mime_type or "image/jpeg"))
            except Exception as e:
                logging.error(f"Failed to load inline image {local_path}: {e}")
        else:
            logging.info(f"Uploading media (SDK): {local_path}...")
            try:
                uploaded_file = client.files.upload(file=local_path)
                while uploaded_file.state.name == "PROCESSING":
                    logging.info("Waiting for video processing...")
                    time.sleep(2)
                    uploaded_file = client.files.get(name=uploaded_file.name)
                if uploaded_file.state.name == "FAILED":
                    logging.error(f"Media processing failed: {uploaded_file.uri}")
                    continue
                items.append(uploaded_file)
            except Exception as e:
                logging.error(f"Failed to upload file {local_path}: {e}")

    return items, temp_files

def generate_content_sdk(client, model_name, prompt, media_items, temperature=0.0, timeout=30):
    """Generate content with timeout to prevent hanging on proxy issues."""
    def _generate():
        contents = [prompt] + media_items
        config = types.GenerateContentConfig(temperature=temperature)
        response = client.models.generate_content(model=model_name, contents=contents, config=config)
        return response.text if response.text else None

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_generate)
            return future.result(timeout=timeout)
    except FuturesTimeoutError:
        logging.error(f"SDK call timed out after {timeout}s ({model_name})")
        return None
    except Exception as e:
        logging.error(f"SDK Error ({model_name}): {e}")
        return None


def cleanup_temp_files(files):
    for f in files:
        if os.path.exists(f):
            try:
                os.remove(f)
            except:
                pass


def main():
    parser = argparse.ArgumentParser(description="Read Media using Antigravity Local Proxy (Gemini Focused)")
    parser.add_argument("prompt", help="Text prompt")
    parser.add_argument("--file", "-f", action="append", help="Path to media file or Google Drive URL")
    parser.add_argument("--type", "-t", default="image", choices=["image", "video", "audio"], help="Media type (hint)")
    parser.add_argument("--temperature", type=float, default=0.0, help="Generation temperature")

    # Keep legacy args for compatibility but they might not be used
    parser.add_argument("--provider", help="Provider preference (optional)")
    parser.add_argument("--key", help="API Key override")

    args = parser.parse_args()

    # Handle Google Drive URLs and YouTube URLs
    drive_temp_files = []
    processed_files = []
    youtube_urls = []  # Track YouTube URLs separately

    if args.file:
        for file_path in args.file:
            if is_youtube_url(file_path):
                logging.info(f"Detected YouTube URL: {file_path}")
                youtube_urls.append(file_path)
                # YouTube URLs are passed directly to Gemini, not as local files
            elif is_drive_url(file_path):
                logging.info(f"Detected Google Drive URL: {file_path}")
                file_id = extract_drive_file_id(file_path)
                if not file_id:
                    logging.error(f"Could not extract file ID from: {file_path}")
                    continue

                local_path = download_from_drive(file_id)
                if local_path:
                    drive_temp_files.append(local_path)
                    processed_files.append(local_path)
                else:
                    logging.error(f"Failed to download Drive file: {file_path}")
            else:
                processed_files.append(file_path)

    # Replace args.file with processed files
    args.file = processed_files if processed_files else None

    success = False

    try:
        # 1. Vector Engine (primary if configured) - using SDK direct
        if PRIMARY_PROVIDER == "vectorengine" and VECTORENGINE_API_KEY:
            client = create_client_vectorengine(VECTORENGINE_API_KEY, VECTORENGINE_BASE_URL)
            if client:
                logging.info("--- Attempting Vector Engine ---")
                media_items, temp_files = load_media_items(processed_files, args.type, client=client, youtube_urls=youtube_urls)
                result = generate_content_sdk(client, VECTORENGINE_MODEL, args.prompt, media_items, args.temperature)
                if result:
                    print("\n--- Output ---\n")
                    print(result)
                    print("\n--------------\n")
                    success = True
                cleanup_temp_files(temp_files)

        # 2. Kie AI (alternative) - skip if YouTube URLs present
        if not success and PRIMARY_PROVIDER == "kie" and not youtube_urls:
            logging.info("--- Attempting Kie AI ---")
            result = generate_content_kie(args.prompt, args.file, args.temperature)
            if result:
                print("\n--- Output ---\n")
                print(result)
                print("\n--------------\n")
                success = True
        elif PRIMARY_PROVIDER == "kie" and youtube_urls:
            logging.info("--- Skipping Kie AI (YouTube URLs not supported) ---")

        # 3. Google Direct / Antigravity Local Proxy (fallback)
        if not success:
            client = create_client_google(GOOGLE_API_KEY)
            if not client and ANTIGRAVITY_API_KEY:
                client = create_client_proxy(ANTIGRAVITY_API_KEY, ANTIGRAVITY_BASE_URL)
            if not client:
                logging.error("No valid API credentials found.")
                cleanup_temp_files(drive_temp_files)
                sys.exit(1)

            logging.info("--- Attempting Google Direct ---")
            media_items, temp_files = load_media_items(processed_files, args.type, client=client, youtube_urls=youtube_urls)
            for model in MODEL_PRIORITY:
                result = generate_content_sdk(client, model, args.prompt, media_items, args.temperature)
                if result:
                    print("\n--- Output ---\n")
                    print(result)
                    print("\n--------------\n")
                    success = True
                    break
            cleanup_temp_files(temp_files)

        if not success:
            logging.error("All providers failed.")
            cleanup_temp_files(drive_temp_files)
            sys.exit(1)
    finally:
        # Always cleanup Drive temp files
        cleanup_temp_files(drive_temp_files)

    sys.exit(0)

if __name__ == "__main__":
    main()
