"""
Music theory engine: Chord parsing, transposing, and scale transposition.
"""
import re
from typing import Optional, List, Tuple
from .models import SongScore, ScoreLine, ScoreMetadata


SHARP_SCALE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLAT_SCALE  = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

NOTE_TO_SEMITONE = {
    "C": 0, "B#": 0,
    "C#": 1, "Db": 1,
    "D": 2,
    "D#": 3, "Eb": 3,
    "E": 4, "Fb": 4,
    "F": 5, "E#": 5,
    "F#": 6, "Gb": 6,
    "G": 7,
    "G#": 8, "Ab": 8,
    "A": 9,
    "A#": 10, "Bb": 10,
    "B": 11, "Cb": 11,
}

# Standard key signatures preference for flats vs sharps
FLAT_KEYS = {"F", "Bb", "Eb", "Ab", "Db", "Gb", "Dm", "Gm", "Cm", "Fm", "Bbm", "Ebm"}

CHORD_PATTERN = re.compile(
    r"^(?P<root>[A-G][b#]?)"
    r"(?P<quality>maj|min|m|M|\+|aug|dim|sus|add)?"
    r"(?P<extension>2|4|5|6|7|9|11|13)?"
    r"(?P<modifier>maj7|min7|m7|M7|m9|maj9|sus2|sus4|dim7|m7b5|7b5|7#5|7b9|7#9|add9|add11|6/9|\(maj7\)|\(m7\))?"
    r"(?:/(?P<bass>[A-G][b#]?))?$"
)

# Loose chord matcher for parsing words in lyrics/chord lines
TOKEN_CHORD_REGEX = re.compile(
    r"\b([A-G][b#]?(?:m|maj|min|M|aug|dim|sus|add)?[0-9]*(?:(?:maj7|min7|m7|M7|m9|maj9|sus2|sus4|dim7|m7b5|add9|6/9))?(?:/[A-G][b#]?)?)\b"
)


def is_valid_chord(token: str) -> bool:
    """Checks if a given string token is a musical chord."""
    token = token.strip("[](),: ")
    if not token or len(token) > 12:
        return False
    # Check if first character is A-G
    if not token[0].isupper() or token[0] not in "ABCDEFG":
        return False
    # If it has digits or chord indicators
    return bool(CHORD_PATTERN.match(token))


def transpose_note(note: str, semitones: int, prefer_flat: bool = False) -> str:
    """Transposes a single note name by given semitones."""
    if note not in NOTE_TO_SEMITONE:
        return note
    idx = (NOTE_TO_SEMITONE[note] + semitones) % 12
    scale = FLAT_SCALE if prefer_flat else SHARP_SCALE
    return scale[idx]


def transpose_chord(chord_str: str, semitones: int, prefer_flat: Optional[bool] = None) -> str:
    """
    Transposes a chord string (e.g. 'G', 'Em7', 'F#m7b5', 'G/B') by N semitones.
    """
    if semitones == 0:
        return chord_str
    
    # Strip any enclosing brackets
    prefix = "[" if chord_str.startswith("[") else ""
    suffix = "]" if chord_str.endswith("]") else ""
    clean_chord = chord_str.strip("[]")
    
    match = CHORD_PATTERN.match(clean_chord)
    if not match:
        # Fallback regex search for root + rest + /bass
        m_fallback = re.match(r"^([A-G][b#]?)(.*?)(?:/([A-G][b#]?))?$", clean_chord)
        if not m_fallback:
            return chord_str
        root, middle, bass = m_fallback.groups()
    else:
        d = match.groupdict()
        root = d.get("root")
        bass = d.get("bass")
        # reconstruct middle from quality, extension, modifier
        middle = clean_chord[len(root): len(clean_chord) - (len(bass) + 1 if bass else 0)]

    if prefer_flat is None:
        # If original root was flat, prefer flat; otherwise sharp
        prefer_flat = "b" in root or (bass and "b" in bass)

    new_root = transpose_note(root, semitones, prefer_flat=prefer_flat)
    new_bass = f"/{transpose_note(bass, semitones, prefer_flat=prefer_flat)}" if bass else ""
    
    return f"{prefix}{new_root}{middle}{new_bass}{suffix}"


def calculate_semitone_shift(from_key: str, to_key: str) -> int:
    """Calculates semitones shift needed to go from from_key to to_key."""
    from_root = re.match(r"^([A-G][b#]?)", from_key.strip())
    to_root = re.match(r"^([A-G][b#]?)", to_key.strip())
    if not from_root or not to_root:
        raise ValueError(f"Invalid key signature: from '{from_key}' to '{to_key}'")
    
    from_semi = NOTE_TO_SEMITONE.get(from_root.group(1), 0)
    to_semi = NOTE_TO_SEMITONE.get(to_root.group(1), 0)
    
    diff = (to_semi - from_semi) % 12
    # Normalize to closest path (-5 to +6)
    if diff > 6:
        diff -= 12
    return diff


def transpose_score(score: SongScore, semitones: int, target_key: Optional[str] = None, prefer_flat: Optional[bool] = None) -> SongScore:
    """
    Returns a new SongScore with all chords transposed by given semitones.
    """
    if semitones == 0 and not target_key:
        return score
    
    # Determine target key and preference
    current_key = score.meta.key or score.meta.original_key or (score.all_chords[0] if score.all_chords else "C")
    
    if target_key:
        semitones = calculate_semitone_shift(current_key, target_key)
        new_key = target_key
    else:
        new_key = transpose_note(current_key, semitones, prefer_flat=bool(prefer_flat))
        
    if prefer_flat is None:
        prefer_flat = new_key in FLAT_KEYS or "b" in new_key

    # Transpose unique chords list
    transposed_all_chords = [transpose_chord(c, semitones, prefer_flat) for c in score.all_chords]
    
    # Transpose lines
    new_lines: List[ScoreLine] = []
    for line in score.lines:
        new_chords = [transpose_chord(c, semitones, prefer_flat) for c in line.chords]
        new_inline = [(pos, transpose_chord(c, semitones, prefer_flat)) for pos, c in line.inline_chords]
        
        # Also replace chords in raw_text / lyrics if chord-only or section header
        if line.is_chord_only or line.is_section_header:
            new_raw = line.raw_text
            for orig_c, trans_c in zip(line.chords, new_chords):
                new_raw = re.sub(r"\b" + re.escape(orig_c) + r"\b", trans_c, new_raw)
        else:
            new_raw = line.raw_text
            
        new_lines.append(
            ScoreLine(
                raw_text=new_raw,
                is_section_header=line.is_section_header,
                section_name=line.section_name,
                is_chord_only=line.is_chord_only,
                chords=new_chords,
                lyrics=line.lyrics,
                inline_chords=new_inline,
            )
        )
        
    # Build updated metadata
    new_meta = ScoreMetadata(
        title=score.meta.title,
        artist=score.meta.artist,
        instrument=score.meta.instrument,
        key=new_key,
        original_key=score.meta.original_key or score.meta.key,
        capo=score.meta.capo,
        tempo=score.meta.tempo,
        time_signature=score.meta.time_signature,
        author=score.meta.author,
        source_url=score.meta.source_url,
        score_id=score.meta.score_id,
        description=score.meta.description,
    )
    
    return SongScore(
        meta=new_meta,
        all_chords=transposed_all_chords,
        lines=new_lines,
        raw_article=score.raw_article,
    )
