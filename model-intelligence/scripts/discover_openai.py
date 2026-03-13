#!/usr/bin/env python3
"""
Discover OpenAI models via API with registry enrichment
Usage: python3 discover_openai.py [--model MODEL_ID]
"""
import os
import sys
import json
from pathlib import Path
from openai import OpenAI
from datetime import datetime

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

def fetch_from_docs(model_id):
    """Fetch model specs from OpenAI docs if not in registry"""
    print(f"\nℹ️  Model not in registry. To get full specs, run:", file=sys.stderr)
    print(f"   python3 scripts/model_info.py {model_id}", file=sys.stderr)
    print(f"   Or add to registry via WebFetch from https://platform.openai.com/docs/models\n", file=sys.stderr)
    return None

def main():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not set")
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    registry = load_registry()

    # Get specific model or list all
    if len(sys.argv) > 1 and sys.argv[1] == '--model':
        model_id = sys.argv[2] if len(sys.argv) > 2 else 'gpt-5.4-pro'
        api_model = client.models.retrieve(model_id)
        registry_model = find_in_registry(model_id, registry)

        # Merge API data with registry data
        result = {
            "id": api_model.id,
            "created": api_model.created,
            "created_date": datetime.fromtimestamp(api_model.created).strftime('%Y-%m-%d'),
            "object": api_model.object,
            "owned_by": api_model.owned_by
        }

        if registry_model:
            result.update({
                "context_window": registry_model.get('context_window'),
                "max_output": registry_model.get('max_output'),
                "vision": registry_model.get('vision'),
                "tier": registry_model.get('tier'),
                "release_date": registry_model.get('release_date'),
                "knowledge_cutoff": registry_model.get('knowledge_cutoff'),
                "cost": registry_model.get('cost')
            })
        else:
            fetch_from_docs(model_id)

        print(json.dumps(result, indent=2))
    else:
        models = client.models.list()
        gpt_models = [m for m in models.data if m.id.startswith('gpt-')]

        # Filter to latest/useful models only (exclude dated snapshots)
        useful_models = []
        for model in gpt_models:
            model_id = model.id
            # Skip dated snapshots (e.g., gpt-4-0613, gpt-5-2025-08-07)
            if any(x in model_id for x in ['-202', '-0', '-1', '-audio-preview', '-realtime-preview', '-search-preview', '-transcribe', '-tts', '-diarize']):
                continue
            # Keep latest versions and main models
            useful_models.append(model)

        # Count models with registry data
        with_registry = sum(1 for m in useful_models if find_in_registry(m.id, registry))
        print(f"Showing {len(useful_models)} latest models ({with_registry} with full specs)\n", file=sys.stderr)

        for model in sorted(useful_models, key=lambda x: x.id):
            registry_model = find_in_registry(model.id, registry)
            context = f" | {registry_model['context_window']:,} ctx" if registry_model and 'context_window' in registry_model else ""
            tier = f" | {registry_model['tier']}" if registry_model and 'tier' in registry_model else ""
            print(f"{model.id:<40} created: {model.created}{tier}{context}")

if __name__ == '__main__':
    main()
