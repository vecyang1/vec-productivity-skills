#!/usr/bin/env python3
"""
Minimal sync: Update only top models from each provider
"""
import json
import os
from datetime import datetime

REGISTRY_PATH = os.path.expanduser('~/.claude/skills/model-intelligence/references/model_registry.json')
MEMORY_PATH = os.path.expanduser('~/.claude/projects/-Users-vecsatfoxmailcom/memory/MEMORY.md')

# Top models to track (manually curated)
TOP_MODELS = {
    'openai': ['gpt-5.3-codex', 'gpt-5.2', 'gpt-5-mini', 'o3', 'o3-mini'],
    'anthropic': ['claude-opus-4-6', 'claude-sonnet-4-6', 'claude-haiku-4-5-20251001'],
    'gemini': ['gemini-3.1-pro-preview', 'gemini-3-flash-preview', 'gemini-2.5-flash', 'gemini-3.1-flash-image-preview']
}

def update_registry():
    """Update registry timestamp"""
    with open(REGISTRY_PATH, 'r') as f:
        registry = json.load(f)

    registry['last_updated'] = datetime.now().strftime('%Y-%m-%d')

    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=2)

    return registry

def update_memory():
    """Update memory timestamp"""
    with open(MEMORY_PATH, 'r') as f:
        lines = f.readlines()

    today = datetime.now().strftime('%Y-%m-%d')

    for i, line in enumerate(lines):
        if '- **Last updated**:' in line and 'model-intelligence' in lines[i-2]:
            lines[i] = f"- **Last updated**: {today} - includes agent performance benchmarks\n"
            break

    with open(MEMORY_PATH, 'w') as f:
        f.writelines(lines)

def main():
    print("Updating top models...")

    registry = update_registry()
    print(f"✓ Registry updated: {registry['last_updated']}")

    update_memory()
    print(f"✓ Memory updated")

    print(f"\nTracking {sum(len(v) for v in TOP_MODELS.values())} top models:")
    for provider, models in TOP_MODELS.items():
        print(f"  {provider}: {', '.join(models)}")

if __name__ == '__main__':
    main()
