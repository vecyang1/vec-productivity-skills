"""
HTML and text parser for Yopu.co chord charts.
"""
import re
import html
from typing import List, Tuple, Optional, Set
from .models import SongScore, ScoreMetadata, ScoreLine
from .transposer import is_valid_chord, TOKEN_CHORD_REGEX


SECTION_KEYWORDS = {
    "前奏", "主歌", "副歌", "间奏", "桥段", "尾奏", "尾声", "转调", "高潮", "过渡", "Solo", "solo",
    "Intro", "intro", "Verse", "verse", "Chorus", "chorus", "Bridge", "bridge", "Outro", "outro",
    "Pre-Chorus", "pre-chorus", "Interlude", "interlude"
}


def clean_html_tags(text: str) -> str:
    """Removes HTML tags and unescapes HTML entities."""
    clean = re.sub(r"<[^>]+>", "", text)
    return html.unescape(clean).strip()


def extract_metadata_from_html(html_text: str, canonical_url: str = "") -> ScoreMetadata:
    """Extracts score title, artist, instrument, key, and capo from page HTML."""
    # Title extraction
    title_match = re.search(r"<title>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
    raw_title = clean_html_tags(title_match.group(1)) if title_match else "Untitled"
    
    # Clean up standard suffix
    clean_title = re.sub(r"\s*(?:吉他和弦谱|吉他谱|和弦谱|尤克里里谱|尤克里里和弦谱|钢琴谱|弹唱谱)\s*$", "", raw_title)
    
    parts = clean_title.split("-", 1)
    if len(parts) == 2:
        title = parts[0].strip()
        artist = parts[1].strip()
    else:
        title = clean_title.strip()
        artist = ""
        
    # Instrument detection
    instrument = "guitar"
    if "尤克里里" in raw_title or "ukulele" in raw_title.lower():
        instrument = "ukulele"
    elif "钢琴" in raw_title or "piano" in raw_title.lower():
        instrument = "piano"
        
    # Meta description
    desc_m = re.search(r"<meta\s+name=[\"']description[\"']\s+content=[\"'](.*?)[\"']", html_text, re.IGNORECASE)
    description = clean_html_tags(desc_m.group(1)) if desc_m else ""
    
    # Extract score ID from URL
    score_id_m = re.search(r"yopu\.co/(?:view|sheet)/([a-zA-Z0-9_-]+)", canonical_url)
    score_id = score_id_m.group(1) if score_id_m else ""
    
    return ScoreMetadata(
        title=title,
        artist=artist,
        instrument=instrument,
        source_url=canonical_url,
        score_id=score_id,
        description=description,
    )


def parse_line(line_text: str) -> ScoreLine:
    """
    Parses a single text line into a ScoreLine.
    Identifies section headers, chord tokens, and lyrical elements.
    """
    line_clean = line_text.strip()
    if not line_clean:
        return ScoreLine(raw_text="")
    
    # Check if section header (e.g. '前奏 G Em Am D', '[主歌1]', 'Intro:')
    first_token = line_clean.split()[0].strip("[]():：")
    is_section = False
    section_name = ""
    for sec in SECTION_KEYWORDS:
        if first_token.startswith(sec) or line_clean.startswith(f"[{sec}") or line_clean.startswith(f"({sec}"):
            is_section = True
            section_name = first_token
            break
            
    # Extract all chords present in the line
    found_chords: List[str] = []
    
    # Check tokens
    tokens = re.split(r"[\s,\|]+", line_clean)
    chord_tokens = [t for t in tokens if is_valid_chord(t)]
    
    # Check if line is chord-only
    is_chord_only = False
    if len(tokens) > 0 and len(chord_tokens) >= len(tokens) * 0.7:
        is_chord_only = True
        found_chords = chord_tokens
    elif is_section:
        found_chords = chord_tokens
    else:
        # Check bracketed chords e.g. [G] or regex tokens
        bracket_chords = re.findall(r"\[([A-G][b#]?[a-zA-Z0-9#/\(\)]*)\]", line_clean)
        valid_brackets = [c for c in bracket_chords if is_valid_chord(c)]
        if valid_brackets:
            found_chords = valid_brackets
        else:
            found_chords = chord_tokens

    # Build inline chords positions if bracketed or detected
    inline_chords: List[Tuple[int, str]] = []
    # If line has bracket notation: [G]吹往南方的风
    if "[" in line_clean and "]" in line_clean:
        pos = 0
        cleaned_lyrics = ""
        i = 0
        while i < len(line_clean):
            if line_clean[i] == "[":
                close = line_clean.find("]", i)
                if close != -1:
                    c_cand = line_clean[i+1:close]
                    if is_valid_chord(c_cand):
                        inline_chords.append((len(cleaned_lyrics), c_cand))
                        i = close + 1
                        continue
            cleaned_lyrics += line_clean[i]
            i += 1
        lyrics = cleaned_lyrics
    else:
        # If standard lyric line with isolated Yopu brackets or tokens
        # Clean rogue closing brackets from Yopu display markers
        lyrics = line_clean.replace("]", "")
        
    return ScoreLine(
        raw_text=line_clean,
        is_section_header=is_section,
        section_name=section_name,
        is_chord_only=is_chord_only,
        chords=found_chords,
        lyrics=lyrics,
        inline_chords=inline_chords,
    )


def parse_yopu_html(html_text: str, canonical_url: str = "") -> SongScore:
    """
    Parses full Yopu HTML page into a SongScore object.
    """
    meta = extract_metadata_from_html(html_text, canonical_url)
    
    # Extract article content
    article_m = re.search(r"<article>(.*?)</article>", html_text, re.DOTALL | re.IGNORECASE)
    raw_article = article_m.group(1).strip() if article_m else ""
    
    lines: List[ScoreLine] = []
    all_chords_set: Set[str] = set()
    all_chords_ordered: List[str] = []
    
    for raw_line in raw_article.splitlines():
        parsed = parse_line(raw_line)
        lines.append(parsed)
        for c in parsed.chords:
            clean_c = c.strip("[]")
            if clean_c and clean_c not in all_chords_set:
                all_chords_set.add(clean_c)
                all_chords_ordered.append(clean_c)
                
    # Detect Key and Capo if present in article lines or meta
    for line in lines[:5]:
        txt = line.raw_text
        key_m = re.search(r"(?:原调|Key|选调|调式)[:：\s]*([1=]?[A-G][b#]?m?)", txt, re.IGNORECASE)
        if key_m:
            detected_key = key_m.group(1).replace("1=", "").strip()
            if not meta.key:
                meta.key = detected_key
        capo_m = re.search(r"(?:变调夹|Capo|capo)[:：\s]*(\d+)", txt, re.IGNORECASE)
        if capo_m:
            meta.capo = int(capo_m.group(1))

    # Default key to first chord root if not explicitly stated
    if not meta.key and all_chords_ordered:
        meta.key = all_chords_ordered[0]
        
    return SongScore(
        meta=meta,
        all_chords=all_chords_ordered,
        lines=lines,
        raw_article=raw_article,
    )
