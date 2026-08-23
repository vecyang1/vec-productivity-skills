#!/usr/bin/env python3
"""
Discover latest Gemini image generation models from Google API
"""
import os
import sys
from dotenv import load_dotenv

try:
    from google import genai
except ImportError:
    print("Error: google-genai library required. Install: pip install google-genai")
    sys.exit(1)

# Load API key from Nano-Banana
load_dotenv(os.path.expanduser('~/.claude/skills/Nano-Banana/.env'))
api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env")
    sys.exit(1)

client = genai.Client(api_key=api_key)
models = client.models.list()

# Filter for image generation models
image_models = []
for model in models:
    name = model.name.lower()
    if 'image' in name and any(x in name for x in ['flash', 'pro', 'exp']):
        image_models.append(model.name)

# Sort by version (newest first)
image_models.sort(reverse=True)

print("Latest Gemini Image Generation Models:")
for m in image_models:
    print(f"  {m}")
