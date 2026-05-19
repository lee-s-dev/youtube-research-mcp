import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import cache
from models import CommentResult, SearchResult, TranscriptResult


class CacheTest(unittest.TestCase):
    def test_cache_path_resolves_relative_to_project(self):
        with patch.dict("os.environ", {"YOUTUBE_RESEARCH_CACHE_DB": "data/test-cache.db"}):
            path = cache.cache_path()
            self.assertTrue(path.is_absolute())
            self.assertTrue(str(path).endswith("data/test-cache.db"))
            # must be resolved relative to the project root, not cwd
            self.assertIn("cache.py", [f.name for f in path.parent.parent.iterdir()])

    def test_transcript_cache_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict("os.environ", {"YOUTUBE_RESEARCH_CACHE_DB": str(Path(tmpdir) / "cache.db")}):
                result = TranscriptResult(
                    video_id="tTw1z10yMCI",
                    url="https://www.youtube.com/watch?v=tTw1z10yMCI",
                    transcript_available=True,
                    transcript_text="hello",
                )

                cache.save_transcript(result)
                cached = cache.get_transcript("tTw1z10yMCI")

                self.assertIsNotNone(cached)
                self.assertTrue(cached.from_cache)
                self.assertEqual(cached.transcript_text, "hello")

    def test_comments_cache_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict("os.environ", {"YOUTUBE_RESEARCH_CACHE_DB": str(Path(tmpdir) / "cache.db")}):
                comments = [
                    CommentResult(
                        comment_id="c1",
                        video_id="tTw1z10yMCI",
                        text="standardization matters",
                    )
                ]

                cache.save_comments("tTw1z10yMCI", 10, "relevance", False, comments)
                cached = cache.get_comments("tTw1z10yMCI", 10, "relevance", False)

                self.assertIsNotNone(cached)
                self.assertEqual(cached[0].text, "standardization matters")

    def test_search_cache_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict("os.environ", {"YOUTUBE_RESEARCH_CACHE_DB": str(Path(tmpdir) / "cache.db")}):
                results = [
                    SearchResult(
                        video_id="tTw1z10yMCI",
                        title="MCP",
                        url="https://www.youtube.com/watch?v=tTw1z10yMCI",
                    )
                ]

                cache.save_search("mcp", 1, None, None, results)
                cached = cache.get_search("mcp", 1, None, None)

                self.assertIsNotNone(cached)
                self.assertEqual(cached[0].video_id, "tTw1z10yMCI")


    def test_transcript_cache_respects_ttl(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict("os.environ", {"YOUTUBE_RESEARCH_CACHE_DB": str(Path(tmpdir) / "cache.db")}):
                result = TranscriptResult(
                    video_id="tTw1z10yMCI",
                    url="https://www.youtube.com/watch?v=tTw1z10yMCI",
                    transcript_available=True,
                    transcript_text="hello",
                )
                cache.save_transcript(result)

                # TTL of 0 days = always expired
                cached = cache.get_transcript("tTw1z10yMCI", ttl_days=0)
                self.assertIsNone(cached)

    def test_transcript_cache_not_expired_within_ttl(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict("os.environ", {"YOUTUBE_RESEARCH_CACHE_DB": str(Path(tmpdir) / "cache.db")}):
                result = TranscriptResult(
                    video_id="tTw1z10yMCI",
                    url="https://www.youtube.com/watch?v=tTw1z10yMCI",
                    transcript_available=True,
                    transcript_text="hello",
                )
                cache.save_transcript(result)

                # Large TTL — should still be valid
                cached = cache.get_transcript("tTw1z10yMCI", ttl_days=365)
                self.assertIsNotNone(cached)


if __name__ == "__main__":
    unittest.main()
