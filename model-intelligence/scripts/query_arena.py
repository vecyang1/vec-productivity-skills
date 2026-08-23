#!/usr/bin/env python3
"""
Query Arena.ai leaderboard data for quick model lookups.

Usage:
    python3 query_arena.py --category text --top 5
    python3 query_arena.py --model "claude-opus-4-6"
"""

import argparse
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REFERENCES_DIR = SCRIPT_DIR.parent / "references"
DATA_PATH = REFERENCES_DIR / "arena_leaderboard.json"

def load_data():
    """Load Arena leaderboard data."""
    if not DATA_PATH.exists():
        print(f"No data found at {DATA_PATH}")
        print("Run: python3 fetch_arena.py --all")
        return None

    with open(DATA_PATH, 'r') as f:
        return json.load(f)

def query_category(data: dict, category: str, top_n: int = 10):
    """Query top models in a category."""
    if category not in data:
        print(f"No data for category: {category}")
        return

    cat_data = data[category]
    print(f"\n{category.upper()} Leaderboard:")
    print(f"URL: {cat_data['url']}")
    print(f"Last updated: {cat_data.get('last_updated', 'Unknown')}\n")

    models = cat_data.get('top_models', [])
    if not models:
        print("⚠️  No model data available. Run fetch_arena.py first.")
        return

    for i, model in enumerate(models[:top_n], 1):
        print(f"{i}. {model['name']}")
        print(f"   ELO: {model['elo']} | Votes: {model.get('votes', 'N/A')}")

def query_model(data: dict, model_name: str):
    """Find a model across all categories."""
    model_lower = model_name.lower()
    found = False

    for category, cat_data in data.items():
        models = cat_data.get('top_models', [])
        for rank, model in enumerate(models, 1):
            if model_lower in model['name'].lower():
                if not found:
                    print(f"\nModel: {model['name']}\n")
                    found = True
                print(f"{category}: Rank #{rank}, ELO {model['elo']}, {model.get('votes', 'N/A')} votes")

    if not found:
        print(f"Model '{model_name}' not found in leaderboard data")

def main():
    parser = argparse.ArgumentParser(description="Query Arena.ai leaderboard")
    parser.add_argument("--category", type=str, help="Category to query")
    parser.add_argument("--model", type=str, help="Model name to search")
    parser.add_argument("--top", type=int, default=10, help="Number of top models")

    args = parser.parse_args()

    data = load_data()
    if not data:
        return

    if args.model:
        query_model(data, args.model)
    elif args.category:
        query_category(data, args.category, args.top)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
