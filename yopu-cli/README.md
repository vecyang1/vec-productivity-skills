# yp — Yopu.co Guitar & Ukulele Chords CLI

A command-line tool and Python SDK to fetch, parse, transpose, and export guitar & ukulele chords and lyrics from [Yopu.co (有谱么)](https://yopu.co).

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)

## Installation

```bash
# Clone or copy into your local environment
git clone https://github.com/vecyang1/vec-productivity-skills.git

# Link binary to PATH
mkdir -p ~/.local/bin
ln -sf $(pwd)/yopu-cli/yp_cli.py ~/.local/bin/yp
ln -sf $(pwd)/yopu-cli/yp_cli.py ~/.local/bin/yopu
```

## Quick Start

```bash
# Fetch score by full URL
yp https://yopu.co/view/aPenOOpb

# Fetch score by ID
yp aPenOOpb

# Transpose up 2 semitones
yp aPenOOpb --transpose +2

# Transpose directly to Key C
yp aPenOOpb --key C

# Export as ChordPro format
yp aPenOOpb --format chordpro

# Export as Markdown file
yp aPenOOpb --format md -o my_score.md

# Machine-readable JSON output
yp aPenOOpb --json
```

## License

Licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](LICENSE).
