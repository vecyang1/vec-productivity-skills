#!/usr/bin/env python3
"""
Model Speed Benchmark Tool
Measures TTFT (Time to First Token) and throughput for AI models.
"""

import time
import sys
import json
from datetime import datetime

def benchmark_summary(model_name: str, ttft: float, tokens: int, total_time: float):
    """Generate a formatted benchmark summary."""
    throughput = tokens / total_time if total_time > 0 else 0

    result = {
        "model": model_name,
        "timestamp": datetime.now().isoformat(),
        "ttft_seconds": round(ttft, 2),
        "total_tokens": tokens,
        "total_time_seconds": round(total_time, 2),
        "throughput_tokens_per_second": round(throughput, 1)
    }

    print(f"\n{'='*50}")
    print(f"  SPEED BENCHMARK RESULTS")
    print(f"{'='*50}")
    print(f"  Model:      {model_name}")
    print(f"  TTFT:       {ttft:.2f}s")
    print(f"  Throughput: {throughput:.1f} t/s")
    print(f"  Total Time: {total_time:.2f}s")
    print(f"  Tokens:     {tokens}")
    print(f"{'='*50}\n")

    # Compare to known benchmarks
    print("  COMPARISON (Gemini Reference):")
    print("  - Gemini 3 Flash:     ~2.4s TTFT, ~50 t/s")
    print("  - Gemini 3.1 Pro:     ~3.9s TTFT, ~30 t/s")
    print("  - Gemini 2.5 Flash:   ~4.3s TTFT, ~88 t/s")
    print(f"{'='*50}\n")

    return result

def manual_benchmark():
    """Guide for manual benchmarking."""
    print("\n" + "="*50)
    print("  MODEL SPEED BENCHMARK")
    print("="*50)
    print()
    print("  For accurate results, measure in a fresh session:")
    print()
    print("  1. Start new session with target model")
    print("  2. Send: 'Write 500 words about AI'")
    print("  3. Measure:")
    print("     - TTFT: Time to first character")
    print("     - Total: Time to completion")
    print("     - Tokens: ~chars/4")
    print()
    print("  REFERENCE BENCHMARKS (Antigravity Proxy):")
    print("  ─────────────────────────────────────────")
    print("  Model                  TTFT    Throughput")
    print("  ─────────────────────────────────────────")
    print("  Gemini 3.1 Pro High    3.90s   ~30 t/s")
    print("  Gemini 3 Flash         2.44s   ~50 t/s")
    print("  Gemini 2.5 Flash       4.30s   ~88 t/s")
    print("  ─────────────────────────────────────────")
    print()
    return None

if __name__ == "__main__":
    manual_benchmark()
