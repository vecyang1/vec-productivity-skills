#!/usr/bin/env python3
"""
Fetch Arena.ai leaderboard data (human-judged ELO rankings).

Usage:
    python3 fetch_arena.py --category text
    python3 fetch_arena.py --all
    python3 fetch_arena.py --top 5
"""

import argparse
import json
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
REFERENCES_DIR = SCRIPT_DIR.parent / "references"
OUTPUT_PATH = REFERENCES_DIR / "arena_leaderboard.json"

CATEGORIES = [
    "text",
    "code",
    "vision",
    "document",
    "text-to-image",
    "image-edit",
    "search",
    "text-to-video",
    "image-to-video",
]

def fetch_category(category: str, top_n: int = 10) -> dict:
    """
    Fetch leaderboard for a category using WebFetch.

    Note: This requires manual WebFetch tool usage in Claude.
    Returns placeholder data structure.
    """
    url = f"https://arena.ai/leaderboard/{category}"

    print(f"⚠️  Fetching {category} requires WebFetch tool")
    print(f"    URL: {url}")
    print(f"    Prompt: Extract top {top_n} models with ELO scores and vote counts")
    print()

    # Placeholder structure
    return {
        "category": category,
        "url": url,
        "last_updated": datetime.now().isoformat(),
        "top_models": [],
        "fetch_method": "manual_webfetch_required"
    }

def load_existing_data() -> dict:
    """Load existing Arena leaderboard data if available."""
    if OUTPUT_PATH.exists():
        with open(OUTPUT_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_data(data: dict):
    """Save Arena leaderboard data."""
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✓ Saved to {OUTPUT_PATH}")

def main():
    parser = argparse.ArgumentParser(description="Fetch Arena.ai leaderboard")
    parser.add_argument("--category", type=str,
                       help=f"Category: {', '.join(CATEGORIES)}")
    parser.add_argument("--all", action="store_true",
                       help="Fetch all categories")
    parser.add_argument("--top", type=int, default=10,
                       help="Number of top models to fetch (default: 10)")
    parser.add_argument("--list", action="store_true",
                       help="List available categories")

    args = parser.parse_args()

    if args.list:
        print("Available categories:")
        for cat in CATEGORIES:
            print(f"  - {cat}")
        return

    data = load_existing_data()

    if args.all:
        categories = CATEGORIES
    elif args.category:
        if args.category not in CATEGORIES:
            print(f"Unknown category: {args.category}")
            print(f"Available: {', '.join(CATEGORIES)}")
            return
        categories = [args.category]
    else:
        parser.print_help()
        return

    for category in categories:
        result = fetch_category(category, args.top)
        data[category] = result

    save_data(data)

    print("\n📝 To populate with real data:")
    print("   Use WebFetch tool on each category URL")
    print("   Extract: model name, ELO score, vote count")
    print("   Update arena_leaderboard.json manually or via script")

if __name__ == "__main__":
    main()
