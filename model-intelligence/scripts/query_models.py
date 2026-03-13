#!/usr/bin/env python3
"""
Query model registry by capabilities, tier, or provider
Usage:
  python3 query_models.py --tier cheap
  python3 query_models.py --vision
  python3 query_models.py --provider openai --tier reasoning
  python3 query_models.py --context-min 500000
  python3 query_models.py --recommend "I need a cheap model with vision for image analysis"
"""
import json
import os
import sys
import argparse

def load_registry():
    registry_path = os.path.join(os.path.dirname(__file__), '../references/model_registry.json')
    with open(registry_path, 'r') as f:
        return json.load(f)

def query_models(provider=None, tier=None, vision=None, context_min=None, max_output_min=None, agent_capable=None):
    """Query models by capabilities"""
    registry = load_registry()
    results = []

    for prov, models in registry.items():
        if prov in ['last_updated', 'evaluation_sources']:
            continue
        if provider and prov != provider:
            continue

        for model in models:
            # Filter by tier
            if tier and tier not in model.get('tier', ''):
                continue

            # Filter by vision
            if vision is not None and model.get('vision') != vision:
                continue

            # Filter by context window
            if context_min and model.get('context_window', 0) < context_min:
                continue

            # Filter by max output
            if max_output_min and model.get('max_output', 0) < max_output_min:
                continue

            # Filter by agent performance
            if agent_capable and 'agent_performance' not in model:
                continue

            results.append({
                'provider': prov,
                'model': model
            })

    return results

def recommend_model(query):
    """Recommend models based on natural language query"""
    query_lower = query.lower()

    # Parse intent
    needs_vision = any(word in query_lower for word in ['image', 'vision', 'visual', 'photo', 'video'])
    needs_cheap = any(word in query_lower for word in ['cheap', 'cost', 'budget', 'affordable', 'economical'])
    needs_powerful = any(word in query_lower for word in ['powerful', 'best', 'smart', 'intelligent', 'complex'])
    needs_reasoning = any(word in query_lower for word in ['reasoning', 'logic', 'think', 'analyze'])
    needs_coding = any(word in query_lower for word in ['code', 'coding', 'programming', 'debug'])
    needs_large_context = any(word in query_lower for word in ['large context', 'long document', '1m', 'million tokens'])

    # Build filters
    filters = {}
    if needs_vision:
        filters['vision'] = True
    if needs_large_context:
        filters['context_min'] = 500000

    # Determine tier preference
    if needs_cheap:
        tier_preference = ['cheap', 'reasoning-cheap', 'balanced']
    elif needs_powerful or needs_reasoning:
        tier_preference = ['powerful', 'reasoning', 'powerful-agentic', 'powerful-reasoning']
    elif needs_coding:
        tier_preference = ['powerful-coding', 'powerful', 'balanced']
    else:
        tier_preference = ['balanced', 'cheap', 'powerful']

    # Query all matching models
    all_results = query_models(**filters)

    # Sort by tier preference
    def tier_score(result):
        tier = result['model'].get('tier', '')
        for i, pref in enumerate(tier_preference):
            if pref in tier:
                return i
        return 999

    all_results.sort(key=tier_score)

    return all_results[:5]  # Top 5 recommendations

def format_model(result):
    """Format model info for display"""
    model = result['model']
    provider = result['provider']

    output = f"\n{provider.upper()}: {model['name']}"
    output += f"\n  Tier: {model.get('tier', 'N/A')}"
    output += f"\n  Description: {model.get('description', 'N/A')}"

    if 'context_window' in model:
        ctx = model['context_window']
        output += f"\n  Context: {ctx:,} tokens ({ctx/1000:.0f}K)"

    if 'max_output' in model:
        output += f"\n  Max Output: {model['max_output']:,} tokens"

    output += f"\n  Vision: {'✓' if model.get('vision') else '✗'}"

    if 'cost' in model:
        output += f"\n  Cost: ${model['cost']['input']}/M input, ${model['cost']['output']}/M output"

    if 'knowledge_cutoff' in model:
        output += f"\n  Knowledge Cutoff: {model['knowledge_cutoff']}"

    if 'agent_performance' in model:
        perf = model['agent_performance']
        output += f"\n  Agent Performance:"
        if 'gdpval_aa_elo' in perf:
            output += f"\n    GDPval-AA ELO: {perf['gdpval_aa_elo']}"
        if 'vending_bench_2_balance' in perf:
            output += f"\n    Vending-Bench 2: ${perf['vending_bench_2_balance']:,.2f}"
        if 'best_for' in perf:
            output += f"\n    Best for: {', '.join(perf['best_for'])}"

    return output

def main():
    parser = argparse.ArgumentParser(description='Query AI model registry')
    parser.add_argument('--provider', choices=['openai', 'anthropic', 'gemini'], help='Filter by provider')
    parser.add_argument('--tier', help='Filter by tier (cheap, balanced, powerful, reasoning, etc.)')
    parser.add_argument('--vision', action='store_true', help='Only models with vision support')
    parser.add_argument('--no-vision', action='store_true', help='Only models without vision')
    parser.add_argument('--context-min', type=int, help='Minimum context window size')
    parser.add_argument('--max-output-min', type=int, help='Minimum max output size')
    parser.add_argument('--agent-capable', action='store_true', help='Only models with agent performance data')
    parser.add_argument('--recommend', type=str, help='Natural language query for recommendations')
    parser.add_argument('--list-all', action='store_true', help='List all models')

    args = parser.parse_args()

    if args.recommend:
        print(f"Recommendations for: \"{args.recommend}\"\n")
        results = recommend_model(args.recommend)
    elif args.list_all:
        results = query_models()
    else:
        vision = True if args.vision else (False if args.no_vision else None)
        results = query_models(
            provider=args.provider,
            tier=args.tier,
            vision=vision,
            context_min=args.context_min,
            max_output_min=args.max_output_min,
            agent_capable=args.agent_capable
        )

    if not results:
        print("No models found matching criteria.")
        return

    print(f"Found {len(results)} model(s):")
    for result in results:
        print(format_model(result))

    registry = load_registry()
    print(f"\n\nRegistry last updated: {registry.get('last_updated', 'Unknown')}")

if __name__ == '__main__':
    main()
