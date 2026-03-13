#!/usr/bin/env python3
"""
Sync from Artificial Analysis API (primary source)
"""
import json
import os
import subprocess
from datetime import datetime

REGISTRY_PATH = os.path.expanduser('~/.claude/skills/model-intelligence/references/model_registry.json')
API_KEY = "aa_ktumuYkNLMYvZdymJrpbvKsJvhYMOrTP"

def fetch_top_models():
    """Fetch top models from AA API"""
    cmd = ['curl', '-s', '-X', 'GET',
           'https://artificialanalysis.ai/api/v2/data/llms/models',
           '-H', f'x-api-key: {API_KEY}']
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return None

    data = json.loads(result.stdout)
    models = data['data']

    # Filter by provider and intelligence
    top = {}
    for m in models:
        creator = m['model_creator']['name']
        intel = m.get('evaluations', {}).get('artificial_analysis_intelligence_index')

        if not intel or creator not in ['OpenAI', 'Anthropic', 'Google']:
            continue

        if creator not in top:
            top[creator] = []

        top[creator].append({
            'name': m['name'],
            'intelligence': intel,
            'context': m.get('evaluations', {}).get('artificial_analysis_intelligence_index'),
            'pricing': m.get('pricing', {})
        })

    # Get top 3 per provider
    for creator in top:
        top[creator] = sorted(top[creator], key=lambda x: x['intelligence'], reverse=True)[:3]

    return top

def main():
    top = fetch_top_models()

    if not top:
        print("✗ Failed to fetch from AA API")
        return

    print("Top models from Artificial Analysis:\n")
    for creator, models in top.items():
        print(f"{creator}:")
        for m in models:
            print(f"  {m['intelligence']:5.1f} | {m['name']}")
        print()

if __name__ == '__main__':
    main()
