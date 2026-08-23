#!/usr/bin/env python3
"""
Discover Claude models via API with registry enrichment
Usage: python3 discover_claude.py [--model MODEL_ID]
"""
import os
import sys
import json
from pathlib import Path
from anthropic import Anthropic

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

def main():
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = Anthropic(api_key=api_key)
    registry = load_registry()

    # Get specific model info from registry
    if len(sys.argv) > 1 and sys.argv[1] == '--model':
        model_id = sys.argv[2] if len(sys.argv) > 2 else 'claude-opus-4-6'
        registry_model = find_in_registry(model_id, registry)

        if registry_model:
            result = {
                "id": model_id,
                "provider": "anthropic",
                "context_window": registry_model.get('context_window'),
                "max_output": registry_model.get('max_output'),
                "vision": registry_model.get('vision'),
                "tier": registry_model.get('tier'),
                "release_date": registry_model.get('release_date'),
                "knowledge_cutoff": registry_model.get('knowledge_cutoff'),
                "cost": registry_model.get('cost'),
                "agent_performance": registry_model.get('agent_performance')
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"Model '{model_id}' not found in registry")
    else:
        # List all Claude models from registry (exclude deprecated)
        anthropic_models = registry.get('anthropic', [])
        deprecated = ['claude-opus-4-5', 'claude-sonnet-4-5-20250929']

        useful_models = [m for m in anthropic_models if m['name'] not in deprecated]

        for model in useful_models:
            context = f" | {model['context_window']:,} ctx" if 'context_window' in model else ""
            tier = f" | {model['tier']}" if 'tier' in model else ""
            print(f"{model['name']:<40}{tier}{context}")

if __name__ == '__main__':
    main()
