#!/usr/bin/env python3
"""
Yopu CLI (yp)
Fetch, parse, transpose, and export guitar & ukulele chords from Yopu.co.

Usage:
    yp https://yopu.co/view/aPenOOpb
    yp aPenOOpb --transpose +2
    yp aPenOOpb --key C --format chordpro
    yp aPenOOpb --format md -o violet_headband.md
    yp aPenOOpb --json
"""
import sys
import os
import argparse
from pathlib import Path

# Ensure yopu package is importable
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from yopu.fetcher import fetch_score_html
from yopu.parser import parse_yopu_html
from yopu.transposer import transpose_score
from yopu.formatter import (
    format_terminal,
    format_chordpro,
    format_markdown,
    format_json,
    format_chords_only,
)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="yp",
        description="Fetch, parse, transpose, and export guitar & ukulele chords from Yopu.co (有谱么)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  yp https://yopu.co/view/aPenOOpb
  yp aPenOOpb --transpose +2
  yp aPenOOpb --key C --format chordpro
  yp aPenOOpb --format md -o sheet.md
  yp aPenOOpb --json
        """,
    )
    parser.add_argument(
        "query",
        help="Yopu score URL or ID (e.g. 'https://yopu.co/view/aPenOOpb' or 'aPenOOpb')",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["terminal", "chordpro", "md", "markdown", "json", "text", "chords"],
        default="terminal",
        help="Output format (default: terminal)",
    )
    parser.add_argument(
        "-t", "--transpose",
        type=int,
        default=0,
        help="Transpose score by N semitones (e.g. +2, -1, 3)",
    )
    parser.add_argument(
        "-k", "--key",
        help="Target musical key to transpose to (e.g. C, D, G, F#)",
    )
    parser.add_argument(
        "-c", "--capo",
        type=int,
        help="Set capo fret position and adjust chords accordingly",
    )
    parser.add_argument(
        "--prefer-flat",
        action="store_true",
        help="Prefer flat accidentals (b) in transposed chords",
    )
    parser.add_argument(
        "--prefer-sharp",
        action="store_true",
        help="Prefer sharp accidentals (#) in transposed chords",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color output in terminal format",
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to save the output file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Shortcut for --format json",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="yp (Yopu CLI) 1.0.0",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Determine format
    fmt = "json" if args.json else args.format.lower()
    if fmt == "markdown":
        fmt = "md"

    # Determine flat/sharp preference
    prefer_flat = None
    if args.prefer_flat:
        prefer_flat = True
    elif args.prefer_sharp:
        prefer_flat = False

    try:
        # 1. Fetch raw HTML
        html_content, canonical_url = fetch_score_html(args.query)

        # 2. Parse score structure
        score = parse_yopu_html(html_content, canonical_url)

        # 3. Handle Capo / Transposition
        semitone_shift = args.transpose
        if args.capo is not None:
            # If capo is applied, chords are shifted downwards to compensate
            semitone_shift -= args.capo
            score.meta.capo = args.capo

        if semitone_shift != 0 or args.key:
            score = transpose_score(
                score,
                semitones=semitone_shift,
                target_key=args.key,
                prefer_flat=prefer_flat,
            )

        # 4. Render output
        if fmt == "json":
            result = format_json(score)
        elif fmt == "chordpro":
            result = format_chordpro(score)
        elif fmt == "md":
            result = format_markdown(score)
        elif fmt == "chords":
            result = format_chords_only(score)
        elif fmt == "text":
            result = format_terminal(score, colorize=False)
        else:  # terminal
            colorize = not args.no_color and sys.stdout.isatty()
            result = format_terminal(score, colorize=colorize)

        # 5. Write to file or stdout
        if args.output:
            out_path = Path(args.output).resolve()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(result)
                f.write("\n")
            print(f"✅ Saved score to {out_path}")
        else:
            print(result)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
