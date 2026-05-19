import unittest

from youtube_utils import (
    clamp_int,
    extract_video_id,
    normalize_languages,
    normalize_query,
    parse_iso8601_duration,
)


class YouTubeUtilsTest(unittest.TestCase):
    def test_extract_video_id_from_common_urls(self):
        self.assertEqual(
            extract_video_id("https://www.youtube.com/watch?v=tTw1z10yMCI"),
            "tTw1z10yMCI",
        )
        self.assertEqual(extract_video_id("https://youtu.be/tTw1z10yMCI"), "tTw1z10yMCI")
        self.assertEqual(
            extract_video_id("https://www.youtube.com/shorts/tTw1z10yMCI"),
            "tTw1z10yMCI",
        )

    def test_extract_video_id_rejects_invalid_values(self):
        with self.assertRaises(ValueError):
            extract_video_id("https://example.com/not-youtube")

    def test_parse_iso8601_duration(self):
        self.assertEqual(parse_iso8601_duration("PT1H2M3S"), 3723)
        self.assertEqual(parse_iso8601_duration("PT5M32S"), 332)
        self.assertIsNone(parse_iso8601_duration(None))

    def test_normalize_query(self):
        self.assertEqual(normalize_query("  mcp   server   tutorial "), "mcp server tutorial")
        with self.assertRaises(ValueError):
            normalize_query("   ")
        with self.assertRaises(ValueError):
            normalize_query("x" * 201)

    def test_normalize_languages(self):
        self.assertEqual(normalize_languages(None), ["ko", "en"])
        self.assertEqual(normalize_languages(["en", "ko", "en-US"]), ["en", "ko", "en-US"])
        with self.assertRaises(ValueError):
            normalize_languages(["../../secret"])

    def test_clamp_int(self):
        self.assertEqual(clamp_int(100, 1, 8), 8)
        self.assertEqual(clamp_int(-1, 1, 8), 1)
        self.assertEqual(clamp_int("bad", 1, 8), 1)


if __name__ == "__main__":
    unittest.main()
