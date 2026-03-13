#!/usr/bin/env python3
"""
Discover Gemini models via API with registry enrichment
Usage: python3 discover_gemini_all.py [--model MODEL_ID]
"""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

try:
    from google import genai
except ImportError:
    print("Error: google-genai library required. Install: pip install google-genai")
    sys.exit(1)

def load_registry():
    registry_path = Path(__file__).parent.parent / 'references' / 'model_registry.json'
    with open(registry_path) as f:
        return json.load(f)

def find_in_registry(model_id, registry):
    for provider, models in registry.items():
        if provider in ['last_updated', 'evaluation_sources']:
            continue
        for model in models:
            if model['name'] == model_id:
                return model
    return None

# Load API key from Nano-Banana
load_dotenv(os.path.expanduser('~/.claude/skills/Nano-Banana/.env'))
api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env")
    sys.exit(1)

client = genai.Client(api_key=api_key)
registry = load_registry()

# Handle specific model query
if len(sys.argv) > 1 and sys.argv[1] == '--model':
    model_id = sys.argv[2] if len(sys.argv) > 2 else 'gemini-3-flash-preview'
    registry_model = find_in_registry(model_id, registry)

    if registry_model:
        result = {
            "id": model_id,
            "provider": "google",
            "context_window": registry_model.get('context_window'),
            "max_output": registry_model.get('max_output'),
            "vision": registry_model.get('vision'),
            "tier": registry_model.get('tier'),
            "release_date": registry_model.get('release_date'),
            "knowledge_cutoff": registry_model.get('knowledge_cutoff'),
            "cost": registry_model.get('cost')
        }
        print(json.dumps(result, indent=2))
        sys.exit(0)
    else:
        print(f"Model '{model_id}' not found in registry")
        sys.exit(1)

models = client.models.list()

# Categorize models
categories = {
    'Text (Flash)': [],
    'Text (Pro)': [],
    'Text (Flash-Lite)': [],
    'Image Generation': [],
    'Experimental': [],
    'Other': []
}

for model in models:
    name = model.name
    name_lower = name.lower()

    # Skip non-gemini models
    if 'gemini' not in name_lower:
        continue

    # Categorize
    if 'image' in name_lower:
        categories['Image Generation'].append(name)
    elif 'exp' in name_lower:
        categories['Experimental'].append(name)
    elif 'flash-lite' in name_lower or 'flash_lite' in name_lower:
        categories['Text (Flash-Lite)'].append(name)
    elif 'flash' in name_lower:
        categories['Text (Flash)'].append(name)
    elif 'pro' in name_lower:
        categories['Text (Pro)'].append(name)
    else:
        categories['Other'].append(name)

# Sort each category (newest first) and limit to top 3
for cat in categories:
    categories[cat].sort(reverse=True)
    # Keep only top 3 latest in each category
    categories[cat] = categories[cat][:3]

# Print results
print("=" * 60)
print("GEMINI MODELS DISCOVERY")
print("=" * 60)

for cat, models in categories.items():
    if models:
        print(f"\n{cat}:")
        for m in models:
            # Extract model name from full path (e.g., "models/gemini-3-flash-preview" -> "gemini-3-flash-preview")
            model_name = m.split('/')[-1] if '/' in m else m
            registry_model = find_in_registry(model_name, registry)
            context = f" | {registry_model['context_window']:,} ctx" if registry_model and 'context_window' in registry_model else ""
            print(f"  {m}{context}")

print("\n" + "=" * 60)
