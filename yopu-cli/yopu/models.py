"""
Data models and structure definitions for Yopu scores.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any


@dataclass
class ScoreMetadata:
    """Metadata of a musical score."""
    title: str
    artist: str = ""
    instrument: str = "guitar"
    key: Optional[str] = None
    original_key: Optional[str] = None
    capo: int = 0
    tempo: Optional[str] = None
    time_signature: Optional[str] = None
    author: Optional[str] = None
    source_url: str = ""
    score_id: str = ""
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "artist": self.artist,
            "instrument": self.instrument,
            "key": self.key,
            "original_key": self.original_key,
            "capo": self.capo,
            "tempo": self.tempo,
            "time_signature": self.time_signature,
            "author": self.author,
            "source_url": self.source_url,
            "score_id": self.score_id,
            "description": self.description,
        }


@dataclass
class ScoreLine:
    """A line of chord/lyrics within a score."""
    raw_text: str
    is_section_header: bool = False
    section_name: str = ""
    is_chord_only: bool = False
    chords: List[str] = field(default_factory=list)
    lyrics: str = ""
    inline_chords: List[Tuple[int, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_text": self.raw_text,
            "is_section_header": self.is_section_header,
            "section_name": self.section_name,
            "is_chord_only": self.is_chord_only,
            "chords": self.chords,
            "lyrics": self.lyrics,
            "inline_chords": self.inline_chords,
        }


@dataclass
class SongScore:
    """Full song sheet data."""
    meta: ScoreMetadata
    all_chords: List[str] = field(default_factory=list)
    lines: List[ScoreLine] = field(default_factory=list)
    raw_article: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "meta": self.meta.to_dict(),
            "all_chords": self.all_chords,
            "lines": [line.to_dict() for line in self.lines],
            "raw_article": self.raw_article,
        }
