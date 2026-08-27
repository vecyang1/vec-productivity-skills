"""
Formatters for rendering Yopu chord scores in terminal, Markdown, ChordPro, and JSON.
"""
import json
from typing import Optional
from .models import SongScore


# ANSI escape sequences for clean terminal colors
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_CYAN = "\033[36m"
ANSI_YELLOW = "\033[33m"
ANSI_GREEN = "\033[32m"
ANSI_MAGENTA = "\033[35m"
ANSI_DIM = "\033[2m"
ANSI_BLUE = "\033[34m"


def format_terminal(score: SongScore, colorize: bool = True) -> str:
    """Formats the song score into a clean terminal-friendly lead sheet."""
    c_bold = ANSI_BOLD if colorize else ""
    c_cyan = ANSI_CYAN if colorize else ""
    c_yellow = ANSI_YELLOW if colorize else ""
    c_green = ANSI_GREEN if colorize else ""
    c_magenta = ANSI_MAGENTA if colorize else ""
    c_dim = ANSI_DIM if colorize else ""
    c_reset = ANSI_RESET if colorize else ""

    out = []
    
    # Title & Header Box
    out.append(f"{c_bold}{c_cyan}================================================================={c_reset}")
    header_title = f"🎵 {score.meta.title}"
    if score.meta.artist:
        header_title += f" - {score.meta.artist}"
    out.append(f"{c_bold}{header_title}{c_reset}")
    
    meta_info = []
    if score.meta.key:
        meta_info.append(f"Key: {score.meta.key}")
    if score.meta.capo > 0:
        meta_info.append(f"Capo: {score.meta.capo}")
    if score.meta.instrument:
        meta_info.append(f"Instrument: {score.meta.instrument.capitalize()}")
    if meta_info:
        out.append(f"{c_dim}{' | '.join(meta_info)}{c_reset}")
    if score.meta.source_url:
        out.append(f"{c_dim}Source: {score.meta.source_url}{c_reset}")
    out.append(f"{c_bold}{c_cyan}================================================================={c_reset}\n")

    # Chords Bar
    if score.all_chords:
        chords_str = " ".join([f"[{c}]" for c in score.all_chords])
        out.append(f"{c_bold}{c_yellow}Chords Used:{c_reset} {c_bold}{chords_str}{c_reset}\n")

    # Song Body
    for line in score.lines:
        raw = line.raw_text
        if not raw:
            out.append("")
            continue
            
        if line.is_section_header:
            out.append(f"{c_bold}{c_magenta}▶ {raw}{c_reset}")
        elif line.is_chord_only:
            out.append(f"  {c_bold}{c_yellow}{raw}{c_reset}")
        elif line.inline_chords:
            # Render chords aligned above lyrics
            chord_line_chars = [" "] * (len(line.lyrics) * 2 + 10)
            for char_idx, chord_name in line.inline_chords:
                pos = min(char_idx * 2, len(chord_line_chars) - len(chord_name) - 1)
                for ci, char in enumerate(chord_name):
                    chord_line_chars[pos + ci] = char
            chord_str = "".join(chord_line_chars).rstrip()
            out.append(f"  {c_bold}{c_yellow}{chord_str}{c_reset}")
            out.append(f"  {line.lyrics}")
        else:
            # Standard lyrical line
            out.append(f"  {line.lyrics}")
            
    out.append(f"\n{c_dim}--- End of Score ---{c_reset}")
    return "\n".join(out)


def format_chordpro(score: SongScore) -> str:
    """Formats the song score in ChordPro standard notation."""
    out = [
        f"{{title: {score.meta.title}}}",
    ]
    if score.meta.artist:
        out.append(f"{{artist: {score.meta.artist}}}")
    if score.meta.key:
        out.append(f"{{key: {score.meta.key}}}")
    if score.meta.capo > 0:
        out.append(f"{{capo: {score.meta.capo}}}")
    if score.meta.source_url:
        out.append(f"{{comment: Source: {score.meta.source_url}}}")
    out.append("")

    for line in score.lines:
        if not line.raw_text:
            out.append("")
            continue
            
        if line.is_section_header:
            out.append(f"{{comment: {line.raw_text}}}")
        elif line.is_chord_only:
            chords_pro = " ".join([f"[{c}]" for c in line.chords])
            out.append(chords_pro)
        elif line.inline_chords:
            # Interleave inline chords into lyrics
            chars = list(line.lyrics)
            for char_idx, chord_name in sorted(line.inline_chords, key=lambda x: x[0], reverse=True):
                if char_idx <= len(chars):
                    chars.insert(char_idx, f"[{chord_name}]")
            out.append("".join(chars))
        else:
            out.append(line.lyrics)

    return "\n".join(out)


def format_markdown(score: SongScore) -> str:
    """Formats the song score into clean GitHub/Obsidian Markdown."""
    out = [
        "---",
        f"title: \"{score.meta.title}\"",
        f"artist: \"{score.meta.artist}\"",
        f"key: \"{score.meta.key or ''}\"",
        f"capo: {score.meta.capo}",
        f"instrument: \"{score.meta.instrument}\"",
        f"source: \"{score.meta.source_url}\"",
        "---",
        "",
        f"# {score.meta.title}" + (f" - {score.meta.artist}" if score.meta.artist else ""),
        "",
        f"> **Key**: `{score.meta.key or 'N/A'}` | **Capo**: `{score.meta.capo}` | **Instrument**: `{score.meta.instrument}`",
        "",
    ]
    
    if score.all_chords:
        out.append("### Chords")
        out.append("`" + "` `".join(score.all_chords) + "`")
        out.append("")
        
    out.append("### Score")
    out.append("```text")
    out.append(score.raw_article)
    out.append("```")
    return "\n".join(out)


def format_json(score: SongScore, indent: int = 2) -> str:
    """Formats the score as structured JSON."""
    return json.dumps(score.to_dict(), ensure_ascii=False, indent=indent)


def format_chords_only(score: SongScore) -> str:
    """Returns only the chord summary."""
    out = [
        f"Song: {score.meta.title} ({score.meta.artist})",
        f"Key: {score.meta.key or 'N/A'}",
        f"Total Unique Chords: {len(score.all_chords)}",
        f"Chords: {', '.join(score.all_chords)}",
    ]
    return "\n".join(out)
