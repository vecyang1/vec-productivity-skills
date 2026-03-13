#!/usr/bin/env python3
"""
Quick benchmark reference tool.

Usage:
    python3 query_benchmarks.py --use-case "coding"
    python3 query_benchmarks.py --domain "finance"
    python3 query_benchmarks.py --model "claude-opus-4-6"
    python3 query_benchmarks.py --list-categories
"""

import argparse
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REFERENCES_DIR = SCRIPT_DIR.parent / "references"
GUIDE_PATH = REFERENCES_DIR / "benchmark_guide.md"
REGISTRY_PATH = REFERENCES_DIR / "model_registry.json"

# Capability-based categories
CAPABILITY_MAP = {
    "multimodal": ["MMMU", "MedScribe"],
    "vision": ["MMMU", "MedScribe"],
    "image": ["MMMU", "MedScribe"],
    "video": ["MMMU"],
    "coding": ["SWE-bench", "LiveCodeBench", "Vibe Code Bench"],
    "agentic-coding": ["SWE-bench", "LiveCodeBench", "Vibe Code Bench"],
    "office": ["APEX-Agents", "GDPval-AA", "Terminal-Bench 2.0"],
    "work": ["APEX-Agents", "GDPval-AA", "Terminal-Bench 2.0"],
    "professional": ["APEX-Agents", "GDPval-AA"],
    "coherence": ["Vending-Bench 2", "Finance Agent v1.1"],
    "long-horizon": ["Vending-Bench 2", "Finance Agent v1.1"],
    "academic": ["GPQA", "MMLU Pro", "AIME"],
    "reasoning": ["GPQA", "MMLU Pro", "AIME"],
}

# Domain-based categories
DOMAIN_MAP = {
    "legal": ["CaseLaw v2", "LegalBench"],
    "law": ["CaseLaw v2", "LegalBench"],
    "finance": ["CorpFin v2", "Finance Agent v1.1", "MortgageTax", "TaxEval v2"],
    "healthcare": ["MedCode", "MedScribe"],
    "medical": ["MedCode", "MedScribe", "MedQA"],
    "math": ["AIME", "ProofBench"],
    "education": ["SAGE"],
}


def list_categories():
    """List all available categories."""
    print("Capability-based categories:")
    for cat in sorted(set(CAPABILITY_MAP.keys())):
        print(f"  - {cat}")

    print("\nDomain-based categories:")
    for cat in sorted(set(DOMAIN_MAP.keys())):
        print(f"  - {cat}")


def query_use_case(use_case: str):
    """Query benchmarks by use case."""
    use_case_lower = use_case.lower()

    # Check capability map
    if use_case_lower in CAPABILITY_MAP:
        benchmarks = CAPABILITY_MAP[use_case_lower]
        print(f"Benchmarks for '{use_case}' (capability-based):")
        for b in benchmarks:
            print(f"  - {b}")
        return

    # Check domain map
    if use_case_lower in DOMAIN_MAP:
        benchmarks = DOMAIN_MAP[use_case_lower]
        print(f"Benchmarks for '{use_case}' (domain-based):")
        for b in benchmarks:
            print(f"  - {b}")
        return

    print(f"No benchmarks found for '{use_case}'")
    print("Use --list-categories to see available categories")


def query_domain(domain: str):
    """Query benchmarks by domain."""
    domain_lower = domain.lower()

    if domain_lower in DOMAIN_MAP:
        benchmarks = DOMAIN_MAP[domain_lower]
        print(f"Benchmarks for {domain} domain:")
        for b in benchmarks:
            print(f"  - {b}")
    else:
        print(f"No benchmarks found for domain '{domain}'")
        print("Available domains:", ", ".join(sorted(DOMAIN_MAP.keys())))


def query_model(model_name: str):
    """Query model performance across benchmarks."""
    if not REGISTRY_PATH.exists():
        print(f"Registry not found: {REGISTRY_PATH}")
        return

    with open(REGISTRY_PATH, 'r') as f:
        registry = json.load(f)

    # Find model in registry
    model_found = False
    for provider, models in registry.items():
        if provider in ["last_updated", "evaluation_sources"]:
            continue

        for model in models:
            if isinstance(model, dict) and model.get("name", "").lower() == model_name.lower():
                model_found = True
                print(f"\nModel: {model['name']}")
                print(f"Tier: {model.get('tier', 'N/A')}")
                print(f"Description: {model.get('description', 'N/A')}")

                if "agent_performance" in model:
                    print("\nAgent Performance:")
                    perf = model["agent_performance"]
                    if "gdpval_aa_elo" in perf:
                        print(f"  GDPval-AA ELO: {perf['gdpval_aa_elo']}")
                    if "vending_bench_2_balance" in perf:
                        print(f"  Vending-Bench 2: ${perf['vending_bench_2_balance']:.2f}")
                    if "best_for" in perf:
                        print(f"  Best for: {', '.join(perf['best_for'])}")

                break

    if not model_found:
        print(f"Model '{model_name}' not found in registry")


def main():
    parser = argparse.ArgumentParser(description="Query benchmark data")
    parser.add_argument("--use-case", type=str, help="Query by use case (e.g., 'coding', 'vision')")
    parser.add_argument("--domain", type=str, help="Query by domain (e.g., 'finance', 'legal')")
    parser.add_argument("--model", type=str, help="Query model performance")
    parser.add_argument("--list-categories", action="store_true", help="List all categories")

    args = parser.parse_args()

    if args.list_categories:
        list_categories()
    elif args.use_case:
        query_use_case(args.use_case)
    elif args.domain:
        query_domain(args.domain)
    elif args.model:
        query_model(args.model)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
