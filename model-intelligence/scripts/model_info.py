#!/usr/bin/env python3
"""
Quick lookup for model specs and pricing.
Usage: python3 model_info.py gpt-5.4
       python3 model_info.py gpt-5-pro
       python3 model_info.py claude-opus-4-6
"""
import json
import sys
from pathlib import Path

def load_registry():
    registry_path = Path(__file__).parent.parent / 'references' / 'model_registry.json'
    with open(registry_path) as f:
        return json.load(f)

def format_price(price):
    """Format price per million tokens"""
    if price is None:
        return "N/A"
    return f"${price:.2f}/M"

def find_model(name):
    registry = load_registry()
    name_lower = name.lower()

    for provider, models in registry.items():
        if provider in ['last_updated', 'evaluation_sources']:
            continue
        for model in models:
            if name_lower in model['name'].lower():
                return provider, model
    return None, None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 model_info.py <model_name>")
        sys.exit(1)

    model_name = sys.argv[1]
    provider, model = find_model(model_name)

    if not model:
        print(f"Model '{model_name}' not found in registry")
        sys.exit(1)

    # Display model info
    print(f"\n{'='*60}")
    print(f"Model: {model['name']}")
    print(f"Provider: {provider.upper()}")
    print(f"{'='*60}")
    print(f"Tier: {model.get('tier', 'N/A')}")
    print(f"Description: {model.get('description', 'N/A')}")
    print(f"\n{'Context & Output:':<20}")
    print(f"  Context Window: {model.get('context_window', 0):,} tokens")
    print(f"  Max Output: {model.get('max_output', 0):,} tokens")
    print(f"  Vision: {'✓' if model.get('vision') else '✗'}")

    # Pricing
    cost = model.get('cost', {})
    print(f"\n{'Pricing (per M tokens):':<20}")
    print(f"  Input: {format_price(cost.get('input'))}")
    print(f"  Cached Input: {format_price(cost.get('cached_input'))}")
    print(f"  Output: {format_price(cost.get('output'))}")

    # Release info
    if 'knowledge_cutoff' in model or 'release_date' in model:
        print(f"\n{'Release Info:':<20}")
        if 'release_date' in model:
            print(f"  Release Date: {model['release_date']}")
        if 'knowledge_cutoff' in model:
            print(f"  Knowledge Cutoff: {model['knowledge_cutoff']}")

    # Agent performance
    if 'agent_performance' in model:
        perf = model['agent_performance']
        print(f"\n{'Agent Performance:':<20}")
        if 'gdpval_aa_elo' in perf:
            print(f"  GDPval-AA ELO: {perf['gdpval_aa_elo']}")
        if 'vending_bench_2_balance' in perf:
            print(f"  Vending-Bench 2: ${perf['vending_bench_2_balance']:,.2f}")

    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
