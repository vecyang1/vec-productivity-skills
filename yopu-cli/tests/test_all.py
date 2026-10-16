"""
Unit tests for yopu-cli.
"""
import sys
import unittest
from pathlib import Path

# Ensure yopu package is importable regardless of working directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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

    def test_terminal_uncolorized_file_save(self):
        from yopu.formatter import format_terminal
        colored = format_terminal(self.score, colorize=True)
        plain = format_terminal(self.score, colorize=False)
        self.assertIn("\033[", colored)
        self.assertNotIn("\033[", plain)

    def test_display_width_alignment(self):
        from yopu.formatter import get_display_width
        self.assertEqual(get_display_width("C"), 1)
        self.assertEqual(get_display_width("发"), 2)
        self.assertEqual(get_display_width("发现站了好久"), 12)
        self.assertEqual(get_display_width("发现站了好久，不 知道要往哪走。"), 31)


class TestYopuCodecV2(unittest.TestCase):
    def test_compute_sheet_t(self):
        from yopu.codec import compute_sheet_t
        st = "2.iHkoVPZYSWTpZq4i.1791549840.oShlIegu.aXYV48kP"
        expected = "JR0CMzAVHz1rYgpZYxcLAXhhOUMPbhJRazlKDzIKCho9WhdDYU5uSR4gBjcCHlg"
        self.assertEqual(compute_sheet_t(st), expected)

    def test_decode_z(self):
        from yopu.codec import encode_z, decode_z
        path = "/api/search/sheets?q=test&page=0&instrument=guitar&v=2"
        encoded = encode_z(path)
        decoded = decode_z(encoded)
        self.assertEqual(decoded, path)


class TestYopuFetcher(unittest.TestCase):
    def test_extract_score_id(self):
        from yopu.fetcher import extract_score_id
        self.assertEqual(extract_score_id("https://yopu.co/view/aXYaaOXZ"), "aXYaaOXZ")
        self.assertEqual(extract_score_id("aXYaaOXZ"), "aXYaaOXZ")

    def test_search_yopu_scores(self):
        from yopu.fetcher import search_yopu_scores
        data = search_yopu_scores("再见青春")
        self.assertIn("results", data)
        self.assertGreater(len(data["results"]), 0)
        self.assertTrue(any("再见青春" in r["title"] for r in data["results"]))

    def test_fetch_target_score_aXYV48kP(self):
        from yopu.fetcher import fetch_score_data
        from yopu.parser import parse_yopu_sheet_data
        data = fetch_score_data("aXYV48kP")
        score = parse_yopu_sheet_data(data)
        self.assertEqual(score.meta.title, "如果你也听说")
        self.assertEqual(score.meta.artist, "张惠妹")
        self.assertIn("G", score.all_chords)
        self.assertIn("Bm7/F#", score.all_chords)
        self.assertGreater(len(score.lines), 15)
        self.assertNotIn("以上为预览版", score.raw_article)

    def test_extract_browser_cookies(self):
        from yopu.fetcher import extract_browser_cookies
        cookies = extract_browser_cookies()
        self.assertIsInstance(cookies, dict)
        if cookies:
            self.assertIn("connect.sid", cookies)

    def test_cookie_persistence(self):
        import tempfile, json, os
        from yopu.fetcher import load_yopu_cookies
        with tempfile.TemporaryDirectory() as tmpdir:
            test_cookie_path = Path(tmpdir) / "cookies.json"
            from unittest.mock import patch
            fake_cookies = {"connect.sid": "fake_sid_123", "c": "fake_c_456"}
            with patch("yopu.fetcher.DEFAULT_COOKIE_FILE", test_cookie_path), \
                 patch("yopu.fetcher.extract_browser_cookies", return_value=fake_cookies):
                loaded = load_yopu_cookies(auto_extract=True, force_refresh=True)
                self.assertEqual(loaded.get("connect.sid"), "fake_sid_123")
                self.assertTrue(test_cookie_path.exists())
                saved = json.loads(test_cookie_path.read_text(encoding="utf-8"))
                self.assertEqual(saved.get("connect.sid"), "fake_sid_123")
                # Assert 0600 file mode
                mode = os.stat(test_cookie_path).st_mode & 0o777
                self.assertEqual(mode, 0o600)

    def test_1password_credential_retrieval(self):
        from yopu.fetcher import get_1password_yopu_credentials
        creds = get_1password_yopu_credentials()
        self.assertIsInstance(creds, dict)
        if creds:
            self.assertIn("connect.sid", creds)

    def test_pickup_notes_and_strophe_separation(self):
        import json
        from yopu.parser import parse_yopu_sheet_data
        sample_path = Path(__file__).resolve().parent.parent / "score_sample.json"
        if sample_path.exists():
            data = json.loads(sample_path.read_text(encoding="utf-8"))
            score = parse_yopu_sheet_data(data)
            # 1. Intro should have 4 bars grouped
            intro_lines = [l.raw_text for l in score.lines if l.is_chord_only and "| G Bm7/F# |" in l.raw_text]
            self.assertTrue(any("| Em Cm | G Bm7/F# | Em Cm |" in l for l in intro_lines))
            # 2. Verse should start with "突然 发现站了好久"
            verse_texts = [l.lyrics for l in score.lines if "发现站了好久" in l.lyrics]
            self.assertTrue(any(t.startswith("突然") for t in verse_texts))
            # 3. Pre-chorus should start with "夜把 心洋葱般剥落"
            pre_chorus = [l.lyrics for l in score.lines if "心洋葱般剥落" in l.lyrics]
            self.assertTrue(any(t.startswith("夜把") for t in pre_chorus))
            # 4. Stanza 2 should not contain duplicate "夜把"
            silent_line = [l.lyrics for l in score.lines if "想我宁可都沉默" in l.lyrics]
            self.assertTrue(silent_line)
            self.assertFalse(any("夜把" in t for t in silent_line))


class TestYopuCLI(unittest.TestCase):
    def test_cli_refresh_auth_flag(self):
        import subprocess
        cli_path = Path(__file__).resolve().parent.parent / "yp_cli.py"
        proc = subprocess.run([sys.executable, str(cli_path), "--refresh-auth"], capture_output=True, text=True, timeout=10)
        self.assertEqual(proc.returncode, 0)
        self.assertTrue("Successfully re-synchronized" in proc.stdout or "No authenticated session" in proc.stdout)


if __name__ == "__main__":
    unittest.main()

