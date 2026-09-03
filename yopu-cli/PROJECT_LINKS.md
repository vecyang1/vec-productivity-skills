# Project Links

This is the multi-root bridge card for `yopu-cli` (Production-grade Lead Sheet Extraction & Transposition Engine).

## Control Card

| Field | Value |
|---|---|
| Project ID | `PL-20260827-yopu-cli` |
| Project Name | Yopu CLI (`yp` / `yopu-cli`) |
| Code Root | `/Users/vecsatfoxmailcom/Documents/A-coding/vec-productivity-skills/yopu-cli` |
| Installed Tool | `~/.local/bin/yp` -> `~/.gemini/antigravity/skills/yopu-cli/yp_cli.py` |
| Sister Tools | `26.08.18-yopu-pdf` (`/Users/vecsatfoxmailcom/Documents/A-coding/26.08.18-yopu-pdf`), `chordverse` (`/Users/vecsatfoxmailcom/Documents/A-coding/2026-08-29 chordverse`) |
| Capability ID | `yopu-cli` |
| Init Gate | `python3 -m compileall yopu` in the code root |
| Operation Gate | `yp --version` or `yp search "晴天"` |
| QA Gate | `python3 -m unittest discover -s tests -p 'test_*.py'` in the code root |

## Callable Surfaces

- `yp search <keyword>` (search Yopu lead sheets with live metadata)
- `yp search <keyword> --pick 1` (auto-pick top result and render lead sheet)
- `yp <id_or_url>` (extract and display lead sheet with chords above lyrics)
- `yp <id_or_url> --transpose +2` (transpose chords by N semitones)
- `yp <id_or_url> --json` (export structured JSON with metadata, sections, chords)
- `yp <id_or_url> --format chordpro` (export ChordPro format)
- `yp <id_or_url> --egress 'ssh:<host>'` (explicit egress relay)
