#!/usr/bin/env python3
"""
Auto-update models from evaluation sources and sync to memory
Token-friendly: only fetches new data, minimal output
"""
import json
import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(SCRIPT_DIR, '../references/model_registry.json')
MEMORY_PATH = os.path.expanduser('~/.claude/projects/-Users-vecsatfoxmailcom/memory/MEMORY.md')

def load_registry():
    with open(REGISTRY_PATH, 'r') as f:
        return json.load(f)

def save_registry(data):
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(data, f, indent=2)

def get_top_agent_models(registry):
    """Extract top agent performers for memory"""
    models = []
    for provider, model_list in registry.items():
        if provider in ['last_updated', 'evaluation_sources']:
            continue
        for model in model_list:
            if 'agent_performance' in model:
                perf = model['agent_performance']
                models.append({
                    'name': model['name'],
                    'provider': provider,
                    'gdpval_elo': perf.get('gdpval_aa_elo', 0),
                    'vending_balance': perf.get('vending_bench_2_balance', 0),
                    'best_for': perf.get('best_for', [])
                })

    # Sort by GDPval ELO (primary) and Vending balance (secondary)
    models.sort(key=lambda x: (x['gdpval_elo'], x['vending_balance']), reverse=True)
    return models[:5]  # Top 5

def update_memory_section(top_models):
    """Update memory with latest agent model rankings"""
    with open(MEMORY_PATH, 'r') as f:
        lines = f.readlines()

    # Find the agent tasks section
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if '**Agent Tasks (Productivity, Long-Horizon, Tool Use)**:' in line:
            start_idx = i
        elif start_idx and line.startswith('**Gemini (Flash models)**:'):
            end_idx = i
            break

    if start_idx is None:
        print("Warning: Could not find agent tasks section in memory")
        return False

    # Build new section
    new_section = ['**Agent Tasks (Productivity, Long-Horizon, Tool Use)**:\n']
    for i, model in enumerate(top_models[:4], 1):  # Top 4 only
        desc = ', '.join(model['best_for'][:2]) if model['best_for'] else 'general'
        metrics = []
        if model['gdpval_elo']:
            metrics.append(f"{model['gdpval_elo']} ELO")
        if model['vending_balance']:
            metrics.append(f"${model['vending_balance']:,.0f}")
        metric_str = f" ({', '.join(metrics)})" if metrics else ""

        if i == 1:
            new_section.append(f"- **Best overall**: `{model['name']}`{metric_str}\n")
        elif i == 2:
            new_section.append(f"- **Most powerful**: `{model['name']}`{metric_str}\n")
        elif 'codex' in model['name'].lower():
            new_section.append(f"- **Coding agents**: `{model['name']}`{metric_str}\n")
        elif 'gemini' in model['name'].lower():
            new_section.append(f"- **Negotiation/persistence**: `{model['name']}`{metric_str}\n")

    new_section.append('\n')

    # Replace section
    lines[start_idx:end_idx] = new_section

    with open(MEMORY_PATH, 'w') as f:
        f.writelines(lines)

    return True

def main():
    registry = load_registry()

    # Update last_updated timestamp
    today = datetime.now().strftime('%Y-%m-%d')
    registry['last_updated'] = today
    save_registry(registry)

    # Get top models and update memory
    top_models = get_top_agent_models(registry)

    if update_memory_section(top_models):
        print(f"✓ Updated registry timestamp: {today}")
        print(f"✓ Updated memory with top {len(top_models)} agent models")
        print("\nTop agent models:")
        for m in top_models[:3]:
            print(f"  {m['name']}: {m['gdpval_elo']} ELO, ${m['vending_balance']:,.0f}")
    else:
        print("✗ Failed to update memory")
        sys.exit(1)

if __name__ == '__main__':
    main()
