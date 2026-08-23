#!/usr/bin/env python3
"""
Fetch latest benchmark scores from various sources.

Usage:
    python3 fetch_benchmarks.py --all              # Fetch all benchmarks
    python3 fetch_benchmarks.py --benchmark mmmu   # Fetch specific benchmark
    python3 fetch_benchmarks.py --update-registry  # Update model_registry.json
"""

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

SCRIPT_DIR = Path(__file__).parent
REFERENCES_DIR = SCRIPT_DIR.parent / "references"
REGISTRY_PATH = REFERENCES_DIR / "model_registry.json"

BENCHMARK_URLS = {
    "mmmu": "https://www.vals.ai/benchmarks/mmmu",
    "swe_bench": "https://www.vals.ai/benchmarks/swe-bench",
    "apex_agents": "https://www.mercor.com/apex/apex-agents-leaderboard/",
    "gdpval_aa": "https://artificialanalysis.ai/evaluations/gdpval-aa",
    "vending_bench": "https://andonlabs.com/evals/vending-bench-2",
    "vals_index": "https://www.vals.ai/benchmarks/vals_index",
}


def fetch_via_claude_webfetch(url: str, prompt: str) -> str:
    """
    Use Claude's WebFetch via subprocess to fetch and parse web content.

    Note: This requires Claude Code CLI to be available.
    Returns the parsed content as string.
    """
    # For now, return instruction to use WebFetch tool manually
    return f"[Manual fetch required: Use WebFetch tool with URL: {url}]"


def fetch_benchmark(benchmark_name: str) -> Dict:
    """Fetch benchmark data from source."""
    url = BENCHMARK_URLS.get(benchmark_name)
    if not url:
        raise ValueError(f"Unknown benchmark: {benchmark_name}")

    print(f"Fetching {benchmark_name} from {url}...")

    # Prompt for extracting leaderboard data
    prompt = """Extract the top 10 model rankings with their scores.
    Return in format: model_name | score | metric_unit
    Focus on the primary metric for this benchmark."""

    result = fetch_via_claude_webfetch(url, prompt)

    return {
        "benchmark": benchmark_name,
        "url": url,
        "data": result,
        "fetch_method": "webfetch",
    }


def parse_benchmark_results(benchmark_name: str, raw_data: str) -> List[Dict]:
    """Parse raw benchmark data into structured format."""
    # This would need custom parsing logic for each benchmark
    # For now, return placeholder
    return [
        {
            "model": "placeholder",
            "score": 0.0,
            "rank": 1,
        }
    ]


def update_registry(benchmark_data: Dict):
    """Update model_registry.json with new benchmark scores."""
    if not REGISTRY_PATH.exists():
        print(f"Registry not found: {REGISTRY_PATH}")
        return

    with open(REGISTRY_PATH, 'r') as f:
        registry = json.load(f)

    # Update last_updated timestamp
    from datetime import datetime
    registry["last_updated"] = datetime.now().strftime("%Y-%m-%d")

    # TODO: Update individual model scores based on benchmark_data

    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=2)

    print(f"Updated registry: {REGISTRY_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Fetch benchmark scores")
    parser.add_argument("--all", action="store_true", help="Fetch all benchmarks")
    parser.add_argument("--benchmark", type=str, help="Fetch specific benchmark")
    parser.add_argument("--update-registry", action="store_true",
                       help="Update model_registry.json with fetched data")
    parser.add_argument("--list", action="store_true",
                       help="List available benchmarks")

    args = parser.parse_args()

    if args.list:
        print("Available benchmarks:")
        for name, url in BENCHMARK_URLS.items():
            print(f"  {name}: {url}")
        return

    if args.all:
        benchmarks = list(BENCHMARK_URLS.keys())
    elif args.benchmark:
        benchmarks = [args.benchmark]
    else:
        parser.print_help()
        return

    results = {}
    for benchmark in benchmarks:
        try:
            data = fetch_benchmark(benchmark)
            results[benchmark] = data
            print(f"✓ Fetched {benchmark}")
        except Exception as e:
            print(f"✗ Failed to fetch {benchmark}: {e}")

    # Save results
    output_path = REFERENCES_DIR / "benchmark_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    if args.update_registry:
        for benchmark, data in results.items():
            update_registry(data)


if __name__ == "__main__":
    main()
