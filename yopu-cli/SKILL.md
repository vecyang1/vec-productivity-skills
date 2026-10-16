---
name: yopu-cli
description: Fetch, parse, transpose, and export guitar & ukulele chords and lyrics from Yopu.co (有谱么) sheets via CLI, Python SDK, or agent automation. Also the owner of Yopu's endpoint gates — use when yopu.co answers an empty HTTP 404, "Yopu returned HTTP 404", or a `/z/` path must be built from another runtime (Cloudflare Worker, JS) and you need to tell a missing session cookie from an IP ban or the TLS-fingerprint gate.
---

# Yopu CLI (`yopu-cli` / `yp`)

A zero-dependency CLI and Python SDK for fetching, extracting, transposing, and exporting guitar and ukulele chord charts from [Yopu.co (有谱么)](https://yopu.co).

## Skill Metadata

- **Origin:** `local`
- **Source:** `skills/yopu-cli`
- **Author:** V
- **Created:** 2026-08-27
- **Updated:** 2026-10-10
- **License:** `AGPL-3.0`
- **Review status:** `reviewed`

## Quick Commands

```bash
# 1. Fetch, Display & Auto-Download Lead Sheet
# Automatically persists "[Title] - [Artist].txt" to current working directory
yp https://yopu.co/view/aXYV48kP
yp aXYV48kP

# 2. Export Selectable Vector PDF
# In CLI: delegates to sister tool yopu-pdf with pinned Python 3.12 runtime
yp https://yopu.co/view/3PbjG3gP --pdf
# (Note: In user interactive zsh, "yp <url>" alias automatically saves PDF to downloads directory)

# 3. Search Songs by Keyword or Artist
yp search "晴天"
yp search "周杰伦" --pick 1   # Auto-select and fetch top result

# 4. Transpose by Semitones (+2 / -1 / -3)
yp aXYaaOXZ --transpose +2

# 5. Transpose to a Specific Key (e.g. C, D, G, F#)
yp https://yopu.co/view/aPenOOpb --key C

# 6. Capo Compensation (e.g. Capo 2)
yp https://yopu.co/view/aPenOOpb --capo 2

# 7. Export to Markdown (also auto-saved on disk with -f md)
yp https://yopu.co/view/aPenOOpb -f md

# 8. Export to ChordPro Format (for OnSong, MobileSheets)
yp https://yopu.co/view/aPenOOpb --format chordpro

# 9. Machine-Readable JSON for Downstream Agents
yp https://yopu.co/view/aPenOOpb --json

# 10. Refresh Session Authentication (1Password & Chrome Cookies)
yp --refresh-auth
```

## Supported Output Formats

| Format | Flag | Description |
| --- | --- | --- |
| `terminal` | `-f terminal` (default) | Colored, human-friendly lead sheet with chords above lyrics (CJK width aligned) |
| `pdf` | `--pdf` or `-f pdf` | Selectable vector PDF lead sheet (delegated to `yopu-pdf`) |
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

### Endpoint gates (updated 2026-10-10)

Yopu gates its endpoints across multiple security layers:

- **Full Sheet Data API v2 (`/api/sheet?code=...&v=2&t=...`)**:
  - Requires computed token `t` derived from `data-model.st` using W-permutation and XOR 22-byte cycle key `SdZWq_H3OXnrFgPLwk9kow`.
  - Without `&t={t}`, the server returns an immediate 15-byte HTTP 404 response.
  - With valid `t` and logged-in session cookie (`connect.sid`), the server returns full payload (~14 KB with 50+ measures, chord definitions `i1f`, and vocal melody track lyrics `t2g[1]`), completely bypassing the preview paywall ("以上为预览版 登录/创建账号").
  - Response is compressed via dual-chunk Brotli (`ar_decompressor.js` / Brotli wasm).

- **Authentication & Cookie Pipeline**:
  - `yopu-cli` automatically retrieves credentials on launch without interactive prompts:
    1. 1Password unattended lookup (`Agent Automation` vault, title `Yopu · Yopu CLI · Production · Session · user@example.com`).
    2. Local Chrome profile SQLite cookie databases (`Profile 2` first, fallback to `Default`).
    3. Cached locally at `~/.config/yopu/cookies.json`. Run `yp --refresh-auth` to force re-extraction.

- **Search** (`/api/search/sheets` via `encode_z` → `/z/<token>`):
  - Needs only the `c=` cookie from `GET /explore`, sent with matching `User-Agent`.
  - Without cookie, responds with empty 404. Bare `/api/search/sheets` is retired.

- **Egress Routing & TLS Protection**:
  - Cloudflare edge TLS fingerprinting can block direct standard `urllib` requests.
  - Automatic fallback chain: Direct connection → Residential proxy / SSH egress (`~/.config/yopu/egress`) → `/ego-browser` zero-facade DOM extraction.
  - To test direct without proxy relay, pass `--egress direct`.

### Visual Alignment Engine (CJK East Asian Width)

- Song lyrics mix Chinese characters (full-width, 2 display columns) with Latin letters, spaces, and punctuation (half-width, 1 display column). Standard character count alignment breaks chord positioning above lyrics.
- `yopu-cli` utilizes `unicodedata.east_asian_width` (`W`/`F` = 2 columns, others = 1 column) to compute true monospace display width, placing chords precisely over their target syllable.
- Supports pickup notes (`cut_bi`) so accompaniment intro chords do not prematurely attach to following vocal phrases.

### Browser Fallback & DOM Parsing Protocol (verified 2026-10-02)

When CLI direct HTTP calls receive an empty 404 or `RemoteDisconnected` due to Yopu's edge TLS fingerprint filter, agents should execute the zero-facade browser fallback via `/ego-browser` (primary default; `chrome-devtools` deprioritized as secondary emergency fallback):

1. **Navigate to score**:
   ```bash
   ego-browser nodejs <<'EOF'
   const task = await taskSpace("yopu-score-extract");
   const page = task.page("p1");
   await page.goto("https://yopu.co/view/<score_id>", { waitUntil: "domcontentloaded" });
   const data = await page.evaluate(() => {
     const svgs = Array.from(document.querySelectorAll('#nier-scroll-view svg'));
     return svgs.map((svg, idx) => {
       const texts = Array.from(svg.querySelectorAll('text')).map(t => ({
         text: t.textContent.trim(),
         x: parseFloat(t.getAttribute('x') || 0),
         y: parseFloat(t.getAttribute('y') || 0),
       })).filter(t => t.text.length > 0);
       const chords = texts.filter(t => t.y < 30 && !['', ''].includes(t.text));
       const lyrics = texts.filter(t => t.y > 165);
       return { measureSvg: idx, chords, lyrics: lyrics.map(l => l.text).join('') };
     });
   });
   console.log(JSON.stringify(data));
   await task.finish({ keep: [] });
   EOF
   ```
2. **Inspect Svelte SVG tree**: The score viewer renders measures as SVGs inside `#nier-scroll-view`:
   - Chord symbols: `<text>` nodes where `y < 30` (ignoring fret icons like ``).
   - Lyrics: `<text>` nodes where `y > 165`.
   - Measure headers / numbers: `<text>` nodes with measure indices (e.g. `1`, `6`, `10`, `14`, `17`, `21`).
3. **Cleanup**: Always close task spaces cleanly via `await task.finish({ keep: [] })` (or `close_page(pageId)` under fallback `chrome-devtools`).
