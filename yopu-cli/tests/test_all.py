"""
Unit tests for yopu-cli.
"""
import unittest
from yopu.models import ScoreMetadata, ScoreLine, SongScore
from yopu.transposer import (
    transpose_chord,
    transpose_note,
    calculate_semitone_shift,
    transpose_score,
    is_valid_chord,
)
from yopu.parser import parse_line, parse_yopu_html, clean_html_tags
from yopu.formatter import (
    format_terminal,
    format_chordpro,
    format_markdown,
    format_json,
    format_chords_only,
)


class TestYopuTransposer(unittest.TestCase):
    def test_chord_validation(self):
        self.assertTrue(is_valid_chord("G"))
        self.assertTrue(is_valid_chord("Em"))
        self.assertTrue(is_valid_chord("Am7"))
        self.assertTrue(is_valid_chord("F#m7b5"))
        self.assertTrue(is_valid_chord("G/B"))
        self.assertTrue(is_valid_chord("Cadd9"))
        self.assertTrue(is_valid_chord("Dsus4"))
        self.assertFalse(is_valid_chord("Hello"))
        self.assertFalse(is_valid_chord("风啊"))

    def test_single_chord_transposition(self):
        # Basic triads
        self.assertEqual(transpose_chord("C", 2), "D")
        self.assertEqual(transpose_chord("G", 2), "A")
        self.assertEqual(transpose_chord("Em", 2), "F#m")
        self.assertEqual(transpose_chord("Am", 2), "Bm")
        self.assertEqual(transpose_chord("D", 2), "E")

        # Downwards shift
        self.assertEqual(transpose_chord("G", -2), "F")
        self.assertEqual(transpose_chord("Em", -2), "Dm")

        # Slash chords
        self.assertEqual(transpose_chord("G/B", 2), "A/C#")
        self.assertEqual(transpose_chord("C/E", 2), "D/F#")

        # Complex extensions
        self.assertEqual(transpose_chord("F#m7b5", 1), "Gm7b5")
        self.assertEqual(transpose_chord("Cadd9", 2), "Dadd9")
        self.assertEqual(transpose_chord("Asus4", 2), "Bsus4")

    def test_semitone_shift_calculation(self):
        self.assertEqual(calculate_semitone_shift("C", "D"), 2)
        self.assertEqual(calculate_semitone_shift("G", "C"), 5)
        self.assertEqual(calculate_semitone_shift("A", "G"), -2)


class TestYopuParser(unittest.TestCase):
    def test_clean_html_tags(self):
        raw = "<h1>Title &amp; Subtitle</h1><p>Test</p>"
        self.assertEqual(clean_html_tags(raw), "Title & SubtitleTest")

    def test_parse_section_line(self):
        line = parse_line("前奏 G Em Am D")
        self.assertTrue(line.is_section_header)
        self.assertEqual(line.section_name, "前奏")
        self.assertEqual(line.chords, ["G", "Em", "Am", "D"])

    def test_parse_lyric_line(self):
        line = parse_line("吹往南方的风啊 如果你遇见一位美丽的姑娘")
        self.assertFalse(line.is_section_header)
        self.assertEqual(line.lyrics, "吹往南方的风啊 如果你遇见一位美丽的姑娘")

    def test_parse_bracketed_line(self):
        line = parse_line("[G]吹往南方的风啊 如果你[Em]遇见一位美丽的[Am]姑娘[D]")
        self.assertEqual(line.chords, ["G", "Em", "Am", "D"])
        self.assertEqual(len(line.inline_chords), 4)
        self.assertEqual(line.lyrics, "吹往南方的风啊 如果你遇见一位美丽的姑娘")


class TestYopuFormatters(unittest.TestCase):
    def setUp(self):
        meta = ScoreMetadata(
            title="紫罗兰发带",
            artist="内蒙汪峰",
            instrument="guitar",
            key="G",
            source_url="https://yopu.co/view/aPenOOpb",
            score_id="aPenOOpb",
        )
        lines = [
            parse_line("前奏 G Em Am D"),
            parse_line("吹往南方的风啊 如果你遇见一位美丽的姑娘"),
        ]
        self.score = SongScore(
            meta=meta,
            all_chords=["G", "Em", "Am", "D"],
            lines=lines,
            raw_article="前奏 G Em Am D\n吹往南方的风啊 如果你遇见一位美丽的姑娘",
        )

    def test_format_terminal(self):
        out = format_terminal(self.score, colorize=False)
        self.assertIn("紫罗兰发带", out)
        self.assertIn("内蒙汪峰", out)
        self.assertIn("[G] [Em] [Am] [D]", out)
        self.assertIn("前奏 G Em Am D", out)

    def test_format_chordpro(self):
        out = format_chordpro(self.score)
        self.assertIn("{title: 紫罗兰发带}", out)
        self.assertIn("{artist: 内蒙汪峰}", out)
        self.assertIn("{key: G}", out)
        self.assertIn("{comment: 前奏 G Em Am D}", out)

    def test_format_markdown(self):
        out = format_markdown(self.score)
        self.assertIn("# 紫罗兰发带 - 内蒙汪峰", out)
        self.assertIn("`G` `Em` `Am` `D`", out)

    def test_format_json(self):
        out = format_json(self.score)
        self.assertIn('"title": "紫罗兰发带"', out)
        self.assertIn('"artist": "内蒙汪峰"', out)


if __name__ == "__main__":
    unittest.main()
