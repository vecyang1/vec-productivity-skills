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


def parse_yopu_sheet_data(data: dict, canonical_url: str = "") -> SongScore:
    """
    Parses decrypted Yopu sheet data (from /api/sheet and scoreUrlV4) into a SongScore.
    """
    score_id = data.get("id") or (canonical_url.split("/")[-1] if canonical_url else "")
    title = data.get("title", "Untitled")
    artist = data.get("artist", "")
    key = data.get("key", "")
    capo = data.get("capo", 0)
    instrument = data.get("type", "guitar")

    meta = ScoreMetadata(
        title=title,
        artist=artist,
        instrument=instrument,
        key=key,
        capo=capo,
        source_url=canonical_url or f"https://yopu.co/view/{score_id}",
        score_id=score_id,
        description=f"{title} - {artist} {instrument} lead sheet",
    )

    all_chords_ordered: List[str] = []
    seen = set()
    for c in data.get("chords", []):
        clean_c = c.strip("[]")
        if clean_c and clean_c not in seen:
            seen.add(clean_c)
            all_chords_ordered.append(clean_c)

    lines: List[ScoreLine] = []

    # 1. Handle browser fallback measures directly if present
    if "browser_measures" in data:
        for bm in data["browser_measures"]:
            if bm.get("section"):
                lines.append(ScoreLine(
                    raw_text=f"[{bm['section']}]",
                    is_section_header=True,
                    section_name=bm["section"],
                    chords=bm.get("chords", []),
                ))
            lyrics = bm.get("lyrics", "").strip()
            chords = bm.get("chords", [])
            if lyrics or chords:
                inline = []
                if chords and lyrics:
                    inline.append((0, chords[0]))
                    if len(chords) > 1 and len(lyrics) > 4:
                        inline.append((len(lyrics) // 2, chords[1]))
                lines.append(ScoreLine(
                    raw_text=lyrics or "  ".join(chords),
                    is_chord_only=not bool(lyrics),
                    chords=chords,
                    lyrics=lyrics,
                    inline_chords=inline,
                ))
        if not meta.key and all_chords_ordered:
            meta.key = all_chords_ordered[0]
        return SongScore(
            meta=meta,
            all_chords=all_chords_ordered,
            lines=lines,
            raw_article="\n".join(bm.get("lyrics", "") for bm in data["browser_measures"]),
        )

    # 2. Check for multi-track score model (score.t2g and score.r8q)
    score_data = data.get("score") if isinstance(data.get("score"), dict) else {}
    r8q = score_data.get("r8q", [])
    t2g = score_data.get("t2g", [])

    chord_track = None
    vocal_track = None
    for tr in t2g:
        jdw = tr.get("jdw", [])
        if jdw and isinstance(jdw[0], dict) and "i1f" in jdw[0]:
            chord_track = jdw[0]
        if jdw and isinstance(jdw[0], dict):
            has_lyrics = any(
                "c8u" in b
                for bar in jdw[0].get("k3i", [])
                for b in bar.get("g78", [{}])[0].get("swk", [])
                if isinstance(b, dict)
            )
            if has_lyrics:
                vocal_track = jdw[0]

    if chord_track and r8q:
        i1f = chord_track.get("i1f", {})
        k0 = chord_track.get("k3i", [])
        k1 = vocal_track.get("k3i", []) if vocal_track else []
        num_bars = len(r8q)

        # Re-derive all_chords_ordered directly from chord_track if available
        derived_chords: List[str] = []
        d_seen = set()
        for bar in k0:
            for beat in bar.get("g78", [{}])[0].get("swk", []):
                sg = beat.get("sg8")
                if sg is not None and str(sg) in i1f:
                    c = i1f[str(sg)].get("uld")
                    if c and c not in d_seen:
                        d_seen.add(c)
                        derived_chords.append(c)
        if derived_chords:
            all_chords_ordered = derived_chords

        def _get_bar_lyrics(b: int) -> List[List[str]]:
            if not k1 or b >= len(k1):
                return []
            return [
                beat.get("c8u")
                for beat in k1[b].get("g78", [{}])[0].get("swk", [])
                if isinstance(beat, dict) and beat.get("c8u")
            ]

        def _get_bar_chords(b: int) -> List[str]:
            b_chords = []
            if b < len(k0):
                for beat in k0[b].get("g78", [{}])[0].get("swk", []):
                    sg = beat.get("sg8")
                    if sg is not None and str(sg) in i1f:
                        c = i1f[str(sg)].get("uld")
                        if c and (not b_chords or b_chords[-1] != c):
                            b_chords.append(c)
            return b_chords

        b_idx = 0
        pending_pickup: List[List[str]] = []
        while b_idx < num_bars:
            # Section Header check
            sec = r8q[b_idx].get("e9q", {}).get("pp4") if isinstance(r8q[b_idx], dict) else None
            if sec:
                lines.append(ScoreLine(
                    raw_text=f"[{sec}]",
                    is_section_header=True,
                    section_name=sec,
                ))

            b_lyric_beats = _get_bar_lyrics(b_idx)
            next_sec = r8q[b_idx + 1].get("e9q", {}).get("pp4") if b_idx + 1 < num_bars else None
            flat_lyr = "".join(c[0] for c in b_lyric_beats)
            is_pure_pickup = bool(b_lyric_beats and len(flat_lyr) <= 3 and next_sec)

            if not b_lyric_beats or is_pure_pickup:
                # Group consecutive instrumental bars (Intro / Solo / Interlude / Outro)
                inst_measures = []
                while b_idx < num_bars:
                    cur_sec = r8q[b_idx].get("e9q", {}).get("pp4") if isinstance(r8q[b_idx], dict) else None
                    if cur_sec and inst_measures:
                        break
                    cur_lyr = _get_bar_lyrics(b_idx)
                    cur_flat = "".join(c[0] for c in cur_lyr)
                    cur_next_sec = r8q[b_idx + 1].get("e9q", {}).get("pp4") if b_idx + 1 < num_bars else None
                    if cur_lyr and not (len(cur_flat) <= 3 and cur_next_sec):
                        break

                    b_chords = _get_bar_chords(b_idx)
                    inst_measures.append(" ".join(b_chords) if b_chords else "-")
                    if cur_lyr and len(cur_flat) <= 3 and cur_next_sec:
                        pending_pickup = cur_lyr
                        b_idx += 1
                        break
                    b_idx += 1
                    if len(inst_measures) == 4:
                        break

                if inst_measures:
                    chunk_text = "| " + " | ".join(inst_measures) + " |"
                    inst_chords = [c for m in inst_measures for c in m.split() if c != "-"]
                    lines.append(ScoreLine(
                        raw_text=chunk_text,
                        is_chord_only=True,
                        chords=inst_chords,
                    ))
            else:
                # Lyrical phrase bars (group 1 or 2 bars per line)
                phrase_bars = [b_idx]
                b_idx += 1
                while b_idx < num_bars and len(phrase_bars) < 2:
                    if r8q[b_idx].get("e9q", {}).get("pp4"):
                        break
                    cur_lyr = _get_bar_lyrics(b_idx)
                    if not cur_lyr:
                        break
                    phrase_bars.append(b_idx)
                    b_idx += 1

                max_strophes = 1
                for pb in phrase_bars:
                    for c8u in _get_bar_lyrics(pb):
                        if len(c8u) > max_strophes:
                            max_strophes = len(c8u)

                # Check trailing pickup on last bar of phrase
                last_pb = phrase_bars[-1]
                last_pb_next_sec = r8q[last_pb + 1].get("e9q", {}).get("pp4") if last_pb + 1 < num_bars else None
                last_lyr_beats = _get_bar_lyrics(last_pb)
                cut_bi = None
                for bi, beat in enumerate(last_lyr_beats):
                    c0 = beat[0] if beat else ""
                    if "。" in c0 or "！" in c0:
                        cut_bi = bi + 1

                next_pending: List[List[str]] = []
                if cut_bi is not None and cut_bi < len(last_lyr_beats):
                    next_pending = last_lyr_beats[cut_bi:]

                strophe_lines_seen = set()
                for s in range(max_strophes):
                    p_prefix = "".join(c[s] if s < len(c) else c[0] for c in pending_pickup).strip()
                    line_lyrics = (p_prefix + " ") if p_prefix else ""
                    inline: List[Tuple[int, str]] = []
                    line_chords: List[str] = []

                    for pb in phrase_bars:
                        pb_chords_in_beats = _get_bar_chords(pb)
                        beats = _get_bar_lyrics(pb)
                        if pb == last_pb and cut_bi is not None and cut_bi < len(beats):
                            beats = beats[:cut_bi]

                        bar_chars = [c[s] if s < len(c) else "" for c in beats]
                        bar_lyr = "".join(bar_chars)

                        # Associate chords with lyric positions
                        if pb_chords_in_beats:
                            for ci, c in enumerate(pb_chords_in_beats):
                                pos = len(line_lyrics) + (len(bar_lyr) * ci // len(pb_chords_in_beats) if bar_lyr else 0)
                                inline.append((pos, c))
                                if c not in line_chords:
                                    line_chords.append(c)
                        line_lyrics += bar_lyr
                        if bar_lyr and not bar_lyr.endswith(("，", "。", " ")):
                            line_lyrics += " "

                    clean_lyrics = line_lyrics.strip()
                    if clean_lyrics and clean_lyrics not in strophe_lines_seen:
                        strophe_lines_seen.add(clean_lyrics)
                        lines.append(ScoreLine(
                            raw_text=clean_lyrics,
                            chords=line_chords,
                            lyrics=clean_lyrics,
                            inline_chords=inline,
                        ))

                pending_pickup = next_pending

        if not meta.key and all_chords_ordered:
            meta.key = all_chords_ordered[0]

        return SongScore(
            meta=meta,
            all_chords=all_chords_ordered,
            lines=lines,
            raw_article="\n".join(l.raw_text for l in lines),
        )

    # 3. Fallback: Parse lyrics into lines if v2 multi-track score model is absent
    raw_lyrics = data.get("lyrics", "")
    sections = []
    if not sections and "v4_data" in data and isinstance(data["v4_data"], dict):
        for mb in data["v4_data"].get("masterBars", []):
            sec = mb.get("section", {}).get("text")
            if sec and sec not in sections:
                sections.append(sec)

    if raw_lyrics:
        sentences = [s.strip() for s in re.split(r"[，。！？\n\r]+", raw_lyrics) if s.strip()]
        chord_idx = 0
        chord_count = len(all_chords_ordered)
        sec_idx = 0
        if sections and sec_idx < len(sections):
            lines.append(ScoreLine(
                raw_text=f"[{sections[sec_idx]}]",
                is_section_header=True,
                section_name=sections[sec_idx],
                chords=all_chords_ordered[:min(4, chord_count)],
            ))
            sec_idx += 1

        for i, sent in enumerate(sentences):
            if i > 0 and i % 4 == 0 and sec_idx < len(sections):
                lines.append(ScoreLine(
                    raw_text=f"[{sections[sec_idx]}]",
                    is_section_header=True,
                    section_name=sections[sec_idx],
                    chords=[],
                ))
                sec_idx += 1

            line_chords = []
            inline = []
            if chord_count > 0:
                c1 = all_chords_ordered[chord_idx % chord_count]
                line_chords.append(c1)
                inline.append((0, c1))
                chord_idx += 1
                if len(sent) > 8:
                    c2 = all_chords_ordered[chord_idx % chord_count]
                    line_chords.append(c2)
                    inline.append((len(sent) // 2, c2))
                    chord_idx += 1

            lines.append(ScoreLine(
                raw_text=sent,
                chords=line_chords,
                lyrics=sent,
                inline_chords=inline,
            ))
    else:
        chunk_size = 4
        for i in range(0, len(all_chords_ordered), chunk_size):
            chunk = all_chords_ordered[i:i + chunk_size]
            lines.append(ScoreLine(
                raw_text="  ".join(chunk),
                is_chord_only=True,
                chords=chunk,
                lyrics="",
            ))

    if not meta.key and all_chords_ordered:
        meta.key = all_chords_ordered[0]

    return SongScore(
        meta=meta,
        all_chords=all_chords_ordered,
        lines=lines,
        raw_article=raw_lyrics,
    )
