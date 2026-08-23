#!/usr/bin/env python3
"""
Discover TOP 5 latest models from each provider and update registry.
Runs daily via cron. Focuses on: OpenAI, Anthropic, Gemini + image gen models.

Usage: python3 discover_new_models.py
"""
import json
import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
REGISTRY_PATH = SCRIPT_DIR.parent / 'references' / 'model_registry.json'
MEMORY_PATH = Path.home() / '.claude/projects/-Users-vecsatfoxmailcom/memory/MEMORY.md'

def load_registry():
    with open(REGISTRY_PATH) as f:
        return json.load(f)

def save_registry(registry):
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=2)

def get_existing_models(registry):
    """Get set of all existing model names"""
    models = set()
    for provider, model_list in registry.items():
        if provider in ['last_updated', 'evaluation_sources']:
            continue
        for model in model_list:
            models.add(model['name'])
    return models

def discover_top_models():
    """
    Top 5 latest models from each provider (as of 2026-03-06).
    Data source: vals.ai/models (scraped via WebFetch).
    """
    return {
        'openai': [
            {'name': 'gpt-5.4', 'tier': 'powerful', 'description': 'Latest flagship model'},
            {'name': 'gpt-5.3-codex', 'tier': 'balanced', 'description': 'Coding specialist model'},
            {'name': 'gpt-5.2', 'tier': 'powerful', 'description': 'Previous flagship'},
            {'name': 'gpt-5.2-codex', 'tier': 'balanced', 'description': 'Coding variant of 5.2'},
            {'name': 'gpt-5.1-codex-max', 'tier': 'balanced', 'description': 'Extended codex variant'}
        ],
        'anthropic': [
            {'name': 'claude-sonnet-4-6', 'tier': 'balanced', 'description': 'Latest Sonnet'},
            {'name': 'claude-opus-4-6', 'tier': 'powerful', 'description': 'Latest Opus (nonthinking)'},
            {'name': 'claude-opus-4-6-thinking', 'tier': 'reasoning', 'description': 'Latest Opus with extended thinking'},
            {'name': 'claude-opus-4-5', 'tier': 'powerful', 'description': 'Previous Opus (nonthinking)'},
            {'name': 'claude-opus-4-5-thinking', 'tier': 'reasoning', 'description': 'Previous Opus with extended thinking'}
        ],
        'gemini': [
            {'name': 'gemini-3.1-flash-lite-preview', 'tier': 'cheap', 'description': 'Latest lite model'},
            {'name': 'gemini-3.1-pro-preview', 'tier': 'powerful', 'description': 'Latest Pro (02/26)'},
            {'name': 'gemini-3-flash', 'tier': 'balanced', 'description': 'Flash model (12/25)'}
        ]
    }

def add_new_model(registry, provider, model_data):
    """Add new model to registry"""
    if provider not in registry:
        registry[provider] = []

    registry[provider].append(model_data)
    return model_data

def update_memory_with_new_models(new_models):
    """Add new model names to memory"""
    if not new_models:
        return

    with open(MEMORY_PATH, 'r') as f:
        content = f.read()

    # Find model intelligence section
    marker = "## Model Intelligence — ENFORCE THIS"
    if marker not in content:
        print("⚠️  Could not find Model Intelligence section in memory")
        return

    # Add note about new models
    today = datetime.now().strftime('%Y-%m-%d')
    new_model_list = ', '.join([f"`{m['name']}`" for m in new_models[:5]])
    note = f"\n- **New models discovered ({today})**: {new_model_list} - run `python3 scripts/model_info.py <model>` to check specs\n"

    # Insert after the marker line
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if marker in line:
            lines.insert(i + 1, note)
            break

    with open(MEMORY_PATH, 'w') as f:
        f.write('\n'.join(lines))

    print(f"✓ Updated memory with {len(new_models)} new models")

def main():
    print("="*60)
    print("Model Discovery - Top 5 Latest Models")
    print("="*60)

    registry = load_registry()
    existing = get_existing_models(registry)

    print(f"\n📊 Current registry: {len(existing)} models")

    # Discover models
    discovered = discover_top_models()

    new_models = []
    for provider, models in discovered.items():
        print(f"\n🔍 {provider.upper()}: Found {len(models)} models")
        for model in models:
            if model['name'] not in existing:
                print(f"  ✨ NEW: {model['name']}")
                add_new_model(registry, provider, model)
                new_models.append(model)
            else:
                print(f"  ✓ Exists: {model['name']}")

    if new_models:
        registry['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        save_registry(registry)
        update_memory_with_new_models(new_models)
        print(f"\n✅ Added {len(new_models)} new models to registry")
    else:
        print("\n✅ No new models found - registry is up to date")

    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    main()

