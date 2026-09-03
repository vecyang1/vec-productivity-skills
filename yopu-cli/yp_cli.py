#!/usr/bin/env python3
"""
Yopu CLI (yp)
Fetch, parse, transpose, and export guitar & ukulele chords from Yopu.co.

Usage:
    yp search "再见青春"
    yp search "汪峰" --pick 1
    yp https://yopu.co/view/aXYaaOXZ
    yp aXYaaOXZ --transpose +2
    yp aXYaaOXZ --key C --format chordpro
    yp aXYaaOXZ --format md -o sheet.md
    yp aXYaaOXZ --json
"""
import sys
import os
import argparse
from pathlib import Path

# Ensure yopu package is importable
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from yopu.fetcher import fetch_score_data, fetch_score_html, search_yopu_scores, extract_score_id, resolve_egress
from yopu.parser import parse_yopu_sheet_data, parse_yopu_html
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
  yp search "再见青春"
  yp search "汪峰" --pick 1
  yp https://yopu.co/view/aXYaaOXZ
  yp aXYaaOXZ --transpose +2
  yp aXYaaOXZ --key C --format chordpro
  yp aXYaaOXZ --format md -o sheet.md
  yp aXYaaOXZ --json
        """,
    )
    parser.add_argument(
        "query",
        help="Yopu score URL, ID, or search query (e.g. 'search 再见青春' or 'aXYaaOXZ')",
    )
    parser.add_argument(
        "extra_terms",
        nargs="*",
        help="Additional search terms if searching",
    )
    parser.add_argument(
        "--pick",
        type=int,
        help="Auto-pick the Nth search result (1-indexed) to fetch directly",
    )
    parser.add_argument(
        "--egress", "--proxy",
        help="Network egress route (e.g. 'ssh:my-vps' or 'socks5://127.0.0.1:7897')",
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
        version="yp (Yopu CLI) 2.0.0",
    )
    return parser.parse_args()


def handle_search(search_term: str, args):
    import json
    data = search_yopu_scores(search_term, egress=args.egress)
    results = data.get("results", [])

    if args.json or args.format == "json":
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    if not results:
        print(f"❌ No scores found on Yopu.co matching: '{search_term}'")
        return

    if args.pick is not None:
        idx = args.pick - 1
        if 0 <= idx < len(results):
            chosen = results[idx]
            print(f"🎯 Auto-selected [{idx + 1}] {chosen['title']} - {chosen['artist']} ({chosen['id']})...\n")
            args.query = chosen["id"]
            fetch_and_render(args)
            return
        else:
            print(f"❌ Pick index {args.pick} out of range (1-{len(results)})", file=sys.stderr)
            sys.exit(1)

    print(f"\n🔍 Found {data['total_count']} matching scores on Yopu.co for \033[1;36m'{search_term}'\033[0m:\n")
    print(f"  {'#':<3} {'ID':<10} {'Song Title':<24} {'Artist':<18} {'Key':<6} {'Verified':<10} {'URL'}")
    print("  " + "─" * 90)
    for idx, r in enumerate(results, 1):
        v_tag = "✅ 认证" if r.get("verified") else "─"
        key_tag = r.get("key") or "-"
        print(f"  {idx:<3} {r['id']:<10} {r['title'][:22]:<24} {r['artist'][:16]:<18} {key_tag:<6} {v_tag:<10} {r['url']}")
    print(f"\n💡 To view a score: \033[1;32myp {results[0]['id']}\033[0m  or  \033[1;32myp search \"{search_term}\" --pick 1\033[0m\n")


def fetch_and_render(args):
    fmt = "json" if args.json else args.format.lower()
    if fmt == "markdown":
        fmt = "md"

    prefer_flat = None
    if args.prefer_flat:
        prefer_flat = True
    elif args.prefer_sharp:
        prefer_flat = False

    # 1. Fetch structured score data
    score = None
    canonical_url = f"https://yopu.co/view/{extract_score_id(args.query)}"
    try:
        data = fetch_score_data(args.query, egress=args.egress)
        score = parse_yopu_sheet_data(data, canonical_url=canonical_url)
    except Exception as exc:
        # Fallback to HTML fetch if API data extraction fails
        try:
            html_content, canonical_url = fetch_score_html(args.query)
            score = parse_yopu_html(html_content, canonical_url)
        except Exception:
            raise exc

    # 2. Handle Capo / Transposition
    semitone_shift = args.transpose
    if args.capo is not None:
        semitone_shift -= args.capo
        score.meta.capo = args.capo

    if semitone_shift != 0 or args.key:
        score = transpose_score(
            score,
            semitones=semitone_shift,
            target_key=args.key,
            prefer_flat=prefer_flat,
        )

    # 3. Render output
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

    # 4. Write to file or stdout
    if args.output:
        out_path = Path(args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(result)
            f.write("\n")
        print(f"✅ Saved score to {out_path}")
    else:
        print(result)


def main():
    args = parse_args()
    q = args.query.strip()

    try:
        # Handle search mode: 'search <term>' or 'find <term>'
        if q.lower() in ("search", "find", "s"):
            terms = " ".join(args.extra_terms).strip()
            if not terms:
                print("❌ Please provide a search term (e.g. yp search '再见青春')", file=sys.stderr)
                sys.exit(1)
            handle_search(terms, args)
            return

        if args.extra_terms:
            full_query = (q + " " + " ".join(args.extra_terms)).strip()
            handle_search(full_query, args)
            return

        clean_id = extract_score_id(q)
        if "/" in q or (len(clean_id) == 8 and clean_id.isalnum() and not any('\u4e00' <= char <= '\u9fff' for char in clean_id)):
            fetch_and_render(args)
        else:
            handle_search(q, args)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
