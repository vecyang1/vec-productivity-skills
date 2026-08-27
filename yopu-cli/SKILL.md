---
name: yopu-cli
description: Fetch, parse, transpose, and export guitar & ukulele chords and lyrics from Yopu.co (有谱么) sheets via CLI, Python SDK, or agent automation.
---

# Yopu CLI (`yopu-cli` / `yp`)

A zero-dependency CLI and Python SDK for fetching, extracting, transposing, and exporting guitar and ukulele chord charts from [Yopu.co (有谱么)](https://yopu.co).

## Skill Metadata

- **Origin:** `local`
- **Source:** `~/.gemini/antigravity/skills/yopu-cli`
- **Author:** V
- **Created:** 2026-08-27
- **Updated:** 2026-08-27
- **License:** `AGPL-3.0`
- **Review status:** `reviewed`

## Quick Commands

```bash
# 1. Fetch & Display Score in Terminal
yp https://yopu.co/view/aPenOOpb
yp aPenOOpb

# 2. Transpose by Semitones (+2 / -1 / -3)
yp https://yopu.co/view/aPenOOpb --transpose +2

# 3. Transpose to a Specific Key (e.g. C, D, G, F#)
yp https://yopu.co/view/aPenOOpb --key C

# 4. Capo Compensation (e.g. Capo 2)
yp https://yopu.co/view/aPenOOpb --capo 2

# 5. Export to ChordPro Format (for OnSong, MobileSheets)
yp https://yopu.co/view/aPenOOpb --format chordpro

# 6. Export to Markdown File
yp https://yopu.co/view/aPenOOpb --format md -o violet_headband.md

# 7. Machine-Readable JSON for Downstream Agents
yp https://yopu.co/view/aPenOOpb --json
```

## Supported Output Formats

| Format | Flag | Description |
| --- | --- | --- |
| `terminal` | `-f terminal` (default) | Colored, human-friendly lead sheet with chords above lyrics |
| `chordpro` | `-f chordpro` | Standard ChordPro notation `[G]lyrics...` for songbook apps |
| `md` / `markdown` | `-f md` | GitHub/Obsidian-compatible Markdown document with frontmatter |
| `json` | `--json` or `-f json` | Structured JSON containing metadata, chord list, and parsed lines |
| `chords` | `-f chords` | Summary of unique chords used in the song |
| `text` | `-f text` | Plain text lead sheet without ANSI color escapes |

## Music Theory & Transposition Engine

- **Full Chromatic Scale**: Transposes all 12 root notes with automatic accidental selection (enharmonics).
- **Complex Chord Shapes**: Handles triads, minor, 7ths, maj7, 9ths, 11ths, 13ths, `sus2`/`sus4`, `dim`/`dim7`, `aug`, `m7b5`, `add9`, and slash chords (e.g. `G/B` -> `A/C#`).
- **Target Key Navigation**: Calculates shortest semitone interval to reach target keys automatically.
- **Accidental Preferences**: Toggle flat/sharp preference via `--prefer-flat` or `--prefer-sharp`.

## Architecture & Design

- **Zero External Dependencies**: Pure Python 3 standard library (`urllib`, `re`, `json`, `argparse`, `dataclasses`).
- **Resilient Transport**: Emulates browser headers with automatic fallback and referer protection.
- **Progressive Context**: Detailed chord syntax specifications live in [references/yopu_chord_format.md](references/yopu_chord_format.md).
