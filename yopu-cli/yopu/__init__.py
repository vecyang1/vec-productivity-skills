"""
Yopu CLI (yp) - Tool to fetch, parse, transpose, and format guitar & ukulele chords from Yopu.co
"""
__version__ = "1.0.0"
__author__ = "V"
__license__ = "AGPL-3.0"

from .models import SongScore, ScoreMetadata, ScoreLine
from .fetcher import fetch_score_html, extract_score_id
from .parser import parse_yopu_html
from .transposer import transpose_score, transpose_chord
from .formatter import format_terminal, format_chordpro, format_markdown, format_json

__all__ = [
    "SongScore",
    "ScoreMetadata",
    "ScoreLine",
    "fetch_score_html",
    "extract_score_id",
    "parse_yopu_html",
    "transpose_score",
    "transpose_chord",
    "format_terminal",
    "format_chordpro",
    "format_markdown",
    "format_json",
]
