"""Live API smoke tests — skipped unless YOUTUBE_API_KEY is set."""
import os
import unittest


REQUIRES_API_KEY = unittest.skipUnless(
    os.getenv("YOUTUBE_API_KEY"),
    "YOUTUBE_API_KEY not set — skipping live API tests",
)


@REQUIRES_API_KEY
class SearchSmokeTest(unittest.TestCase):
    def test_search_returns_results(self):
        from youtube_research_mcp.youtube_utils import search_videos

        results = search_videos("python tutorial", max_results=2)
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertRegex(r.video_id, r"^[a-zA-Z0-9_-]{11}$")
            self.assertIsNotNone(r.title)

    def test_search_filter_removes_shorts(self):
        from youtube_research_mcp.youtube_utils import filter_search_quality, search_videos

        raw = search_videos("python shorts", max_results=5)
        filtered = filter_search_quality(raw, exclude_shorts=True)
        for r in filtered:
            if r.duration_seconds is not None:
                self.assertGreater(r.duration_seconds, 90)


@REQUIRES_API_KEY
class TranscriptSmokeTest(unittest.TestCase):
    # "Me at the zoo" — first YouTube video, stable, known to have auto-captions
    KNOWN_VIDEO_ID = "jNQXAC9IVRw"

    def test_fetch_transcript_returns_result(self):
        from youtube_research_mcp.youtube_utils import fetch_transcript

        result = fetch_transcript(self.KNOWN_VIDEO_ID)
        self.assertEqual(result.video_id, self.KNOWN_VIDEO_ID)
        self.assertIsInstance(result.transcript_available, bool)

    def test_fetch_transcript_when_available(self):
        from youtube_research_mcp.youtube_utils import fetch_transcript

        result = fetch_transcript(self.KNOWN_VIDEO_ID)
        if result.transcript_available:
            self.assertIsNotNone(result.transcript_text)
            self.assertGreater(len(result.transcript_text), 0)
            self.assertIsNotNone(result.safety_notice)


@REQUIRES_API_KEY
class CommentSmokeTest(unittest.TestCase):
    KNOWN_VIDEO_ID = "jNQXAC9IVRw"

    def test_fetch_comments_returns_list(self):
        from youtube_research_mcp.youtube_utils import fetch_comments

        comments = fetch_comments(self.KNOWN_VIDEO_ID, max_comments=5)
        self.assertIsInstance(comments, list)
        for c in comments:
            self.assertIsNotNone(c.comment_id)
            self.assertIsNotNone(c.text)
            self.assertIsNotNone(c.safety_notice)


@REQUIRES_API_KEY
class VideoMetadataSmokeTest(unittest.TestCase):
    KNOWN_VIDEO_ID = "jNQXAC9IVRw"

    def test_get_video_metadata(self):
        from youtube_research_mcp.youtube_utils import get_video_metadata

        metadata = get_video_metadata(self.KNOWN_VIDEO_ID)
        self.assertEqual(metadata.video_id, self.KNOWN_VIDEO_ID)
        self.assertIsNotNone(metadata.title)


if __name__ == "__main__":
    unittest.main()
