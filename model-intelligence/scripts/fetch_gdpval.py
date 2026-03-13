#!/usr/bin/env python3
"""
Fetch latest GDPval-AA rankings from Artificial Analysis
Usage:
  export AA_API_KEY="your_key"  # Get from artificialanalysis.ai
  python3 fetch_gdpval.py
"""
import json
import os
import sys
import subprocess

def fetch_rankings():
    """Fetch via API if key available, else return cached data"""
    api_key = os.getenv('AA_API_KEY')

    if api_key:
        cmd = ['curl', '-s', '-X', 'GET',
               'https://artificialanalysis.ai/api/v2/data/llms/models',
               '-H', f'x-api-key: {api_key}']
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                models = []
                for m in data:
                    evals = m.get('evaluations', {})
                    gdpval = evals.get('gdpval_aa', {})
                    if gdpval and 'elo' in gdpval:
                        models.append({
                            'name': m.get('name'),
                            'elo': gdpval['elo'],
                            'provider': m.get('provider')
                        })
                return sorted(models, key=lambda x: x['elo'], reverse=True)
            except:
                pass

    # Fallback: cached data from 2026-03-04
    return [
        {'name': 'Claude Sonnet 4.6 (Adaptive Reasoning, Max Effort)', 'elo': 1633, 'provider': 'Anthropic'},
        {'name': 'Claude Opus 4.6 (Adaptive Reasoning, Max Effort)', 'elo': 1606, 'provider': 'Anthropic'},
        {'name': 'Claude Opus 4.6 (Non-reasoning, High Effort)', 'elo': 1579, 'provider': 'Anthropic'},
        {'name': 'Claude Sonnet 4.6 (Non-reasoning, High Effort)', 'elo': 1553, 'provider': 'Anthropic'},
        {'name': 'GPT-5.3 Codex (xhigh)', 'elo': 1462, 'provider': 'OpenAI'},
        {'name': 'GPT-5.2 (xhigh)', 'elo': 1462, 'provider': 'OpenAI'},
    ]

def main():
    models = fetch_rankings()
    method = "API" if os.getenv('AA_API_KEY') else "cached"

    print(f"Top GDPval-AA models ({method}):\n")
    for i, m in enumerate(models[:10], 1):
        print(f"{i}. {m['name']}: {m['elo']} ELO")

    print(f"\nSource: https://artificialanalysis.ai/evaluations/gdpval-aa")
    if method == "cached":
        print("Tip: Set AA_API_KEY for live data (1000 req/day free)")

if __name__ == '__main__':
    main()
