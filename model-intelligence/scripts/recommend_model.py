#!/usr/bin/env python3
"""
Get latest model recommendations by purpose/industry.
Hybrid approach: Vals AI (latest) + AA API (stable).

Usage:
    python3 recommend_model.py --purpose "coding"
    python3 recommend_model.py --industry "finance"
    python3 recommend_model.py --priority "work"  # Personal priorities
    python3 recommend_model.py --latest  # Show newest models
"""

import argparse
import subprocess
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REFERENCES_DIR = SCRIPT_DIR.parent / "references"

# Purpose → Benchmark mapping
PURPOSE_MAP = {
    "coding": {"benchmarks": ["SWE-bench", "LiveCodeBench"], "weight": "agentic"},
    "vision": {"benchmarks": ["MMMU"], "weight": "multimodal"},
    "office": {"benchmarks": ["APEX-Agents", "Arena.ai Code"], "weight": "agentic"},
    "writing": {"benchmarks": ["Arena.ai Text"], "weight": "creative"},
    "reasoning": {"benchmarks": ["GPQA", "MMLU Pro"], "weight": "academic"},
}

# Industry → Domain mapping
INDUSTRY_MAP = {
    "finance": ["CorpFin", "TaxEval", "Finance Agent"],
    "legal": ["CaseLaw", "LegalBench"],
    "healthcare": ["MedCode", "MedScribe", "MedQA"],
    "education": ["SAGE"],
}

# Personal priorities mapping
PRIORITY_MAP = {
    "work": {
        "name": "Daily Work / Productivity / Money",
        "models": ["Claude Opus 4.6", "Claude Sonnet 4.6", "GPT 5.4 xHigh"],
        "benchmarks": ["Vending-Bench 2", "GDPval-AA", "APEX-Agents"]
    },
    "multimodal": {
        "name": "Video/Image Understanding",
        "models": ["Gemini 3.1 Pro", "Gemini 3 Flash", "Gemini 3 Pro"],
        "benchmarks": ["Arena.ai Vision", "MMMU"]
    },
    "writing": {
        "name": "Social Media / Articles (Human-like)",
        "models": ["Claude Opus 4.6", "Gemini 3.1 Pro", "Claude Sonnet 4.6"],
        "benchmarks": ["Arena.ai Text"]
    },
    "image-edit": {
        "name": "Image Editing",
        "models": ["Gemini 3.1 Flash Image", "ChatGPT Image Latest"],
        "benchmarks": ["Arena.ai Image Edit"]
    },
    "frontend": {
        "name": "Frontend Web Design",
        "models": ["Gemini 3.1 Pro", "GPT 5.4", "Claude Opus 4.6"],
        "benchmarks": ["Vibe Code Bench", "Arena.ai Code"]
    },
    "healthcare": {
        "name": "Healthcare (Low Hallucination)",
        "models": ["Claude Opus 4.6", "Gemini 3.1 Pro", "GPT 5.1"],
        "benchmarks": ["MedQA", "MedScribe"]
    }
}

def get_latest_from_vals():
    """Fetch latest top models from Vals AI (requires manual WebFetch)"""
    print("⚠️  Latest models require WebFetch from Vals AI")
    print("    Run: Use WebFetch tool on https://www.vals.ai/benchmarks/vals_index")
    print("    Or check: https://www.vals.ai/models")
    return None

def get_stable_from_aa():
    """Get stable models from AA API"""
    try:
        result = subprocess.run(
            ["/usr/bin/python3", str(SCRIPT_DIR / "sync_from_aa.py")],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout if result.returncode == 0 else None
    except Exception:
        return None

def recommend_by_purpose(purpose: str):
    """Recommend models by purpose"""
    purpose_lower = purpose.lower()

    if purpose_lower not in PURPOSE_MAP:
        print(f"Unknown purpose: {purpose}")
        print(f"Available: {', '.join(PURPOSE_MAP.keys())}")
        return

    config = PURPOSE_MAP[purpose_lower]
    print(f"\n📊 Model recommendations for: {purpose}")
    print(f"Relevant benchmarks: {', '.join(config['benchmarks']) if config['benchmarks'] else 'No formal benchmarks'}\n")

    # Hardcoded recommendations (from benchmark_guide.md)
    recommendations = {
        "coding": [
            ("Claude Opus 4.6", "77.2% SWE-bench, best for autonomous debugging"),
            ("GPT 5.3 Codex", "Top coding model, 54.0 AA Intelligence"),
            ("Claude Sonnet 4.6", "Balanced cost-performance"),
        ],
        "vision": [
            ("Gemini 3.1 Pro", "88.2% MMMU, best multimodal"),
            ("Gemini 3 Flash", "87.6% MMMU, faster"),
            ("GPT 5.4", "87.5% MMMU"),
        ],
        "office": [
            ("GPT 5.4 xHigh", "35.9% APEX-Agents"),
            ("Claude Sonnet 4.6", "1633 ELO GDPval-AA"),
            ("Claude Opus 4.6", "1606 ELO, long-horizon"),
        ],
        "writing": [
            ("Claude Opus 4.6", "Natural prose, narrative coherence"),
            ("GPT 5.2", "Versatile, style matching"),
            ("Claude Sonnet 4.6", "Conversational, concise"),
        ],
        "reasoning": [
            ("Claude Opus 4.6", "91.7% GPQA, 96.7% AIME"),
            ("Gemini 3.1 Pro", "Strong academic reasoning"),
            ("GPT 5.2", "Balanced reasoning capability"),
        ],
    }

    if purpose_lower in recommendations:
        for i, (model, desc) in enumerate(recommendations[purpose_lower], 1):
            print(f"{i}. {model}")
            print(f"   {desc}\n")

def recommend_by_industry(industry: str):
    """Recommend models by industry"""
    industry_lower = industry.lower()

    if industry_lower not in INDUSTRY_MAP:
        print(f"Unknown industry: {industry}")
        print(f"Available: {', '.join(INDUSTRY_MAP.keys())}")
        return

    benchmarks = INDUSTRY_MAP[industry_lower]
    print(f"\n🏢 Model recommendations for: {industry}")
    print(f"Relevant benchmarks: {', '.join(benchmarks)}\n")

    # Domain-specific recommendations
    recommendations = {
        "finance": [
            ("Claude Sonnet 4.6", "Top on Finance Agent, TaxEval"),
            ("Gemini 3.1 Pro", "Strong on CorpFin, MortgageTax"),
            ("Claude Opus 4.6", "Best for complex financial analysis"),
        ],
        "legal": [
            ("GPT 5.1", "Top on CaseLaw v2"),
            ("Gemini 3.1 Pro", "Top on LegalBench"),
            ("Claude Opus 4.6", "Strong legal reasoning"),
        ],
        "healthcare": [
            ("Gemini 3.1 Pro", "Top on MedCode"),
            ("GPT 5.1", "Top on MedScribe"),
            ("Claude Opus 4.6", "96.1% MedQA"),
        ],
        "education": [
            ("Claude Opus 4.5", "Top on SAGE"),
            ("Claude Sonnet 4.6", "Balanced for education"),
        ],
    }

    if industry_lower in recommendations:
        for i, (model, desc) in enumerate(recommendations[industry_lower], 1):
            print(f"{i}. {model}")
            print(f"   {desc}\n")

def recommend_by_priority(priority: str):
    """Recommend models by personal priority."""
    priority_lower = priority.lower()

    if priority_lower not in PRIORITY_MAP:
        print(f"Unknown priority: {priority}")
        print(f"Available: {', '.join(PRIORITY_MAP.keys())}")
        return

    config = PRIORITY_MAP[priority_lower]
    print(f"\n🎯 {config['name']}")
    print(f"Relevant benchmarks: {', '.join(config['benchmarks'])}\n")

    for i, model in enumerate(config['models'], 1):
        print(f"{i}. {model}")

def main():
    parser = argparse.ArgumentParser(description="Get model recommendations")
    parser.add_argument("--purpose", type=str, help="Purpose: coding, vision, office, writing, reasoning")
    parser.add_argument("--industry", type=str, help="Industry: finance, legal, healthcare, education")
    parser.add_argument("--priority", type=str, help="Personal priority: work, multimodal, writing, image-edit, frontend, healthcare")
    parser.add_argument("--latest", action="store_true", help="Show latest models (requires WebFetch)")

    args = parser.parse_args()

    if args.latest:
        get_latest_from_vals()
    elif args.priority:
        recommend_by_priority(args.priority)
    elif args.purpose:
        recommend_by_purpose(args.purpose)
    elif args.industry:
        recommend_by_industry(args.industry)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
