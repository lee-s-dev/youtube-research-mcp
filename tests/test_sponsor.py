import unittest

from youtube_research_mcp.youtube_utils import detect_sponsor_signals


class DetectSponsorSignalsTest(unittest.TestCase):
    def test_detects_sponsored_by(self):
        signals = detect_sponsor_signals("This video is sponsored by Squarespace.")
        self.assertIn("sponsored by", signals)

    def test_detects_use_code(self):
        signals = detect_sponsor_signals("Use my code PYTHON20 for 20% off.")
        self.assertIn("use my code", signals)

    def test_detects_multiple(self):
        signals = detect_sponsor_signals(
            "Thanks to our sponsor. Use code SAVE10 at checkout."
        )
        self.assertIn("thanks to our sponsor", signals)
        self.assertIn("use code", signals)

    def test_empty_text_returns_empty(self):
        self.assertEqual(detect_sponsor_signals(""), [])
        self.assertEqual(detect_sponsor_signals(None), [])

    def test_clean_transcript_returns_empty(self):
        signals = detect_sponsor_signals(
            "Today we build a REST API using FastAPI. Let's start by installing the library."
        )
        self.assertEqual(signals, [])

    def test_case_insensitive(self):
        signals = detect_sponsor_signals("SPONSORED BY NordVPN.")
        self.assertIn("sponsored by", signals)


if __name__ == "__main__":
    unittest.main()
