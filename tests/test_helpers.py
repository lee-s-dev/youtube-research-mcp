"""Tests for server-level helpers: _check_duration, _truncate_transcript."""
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import TranscriptResult, VideoMetadata
from server import _check_duration, _truncate_transcript


def _video(duration=None):
    return VideoMetadata(video_id="aaaaaaaaaaa", url="https://www.youtube.com/watch?v=aaaaaaaaaaa", duration_seconds=duration)


def _transcript(text="hello world"):
    return TranscriptResult(
        video_id="aaaaaaaaaaa",
        url="https://www.youtube.com/watch?v=aaaaaaaaaaa",
        transcript_available=True,
        transcript_text=text,
    )


class CheckDurationTest(unittest.TestCase):
    def test_too_short(self):
        self.assertEqual(_check_duration(_video(60), 120, 7200), "too_short")

    def test_too_long(self):
        self.assertEqual(_check_duration(_video(9000), 120, 7200), "too_long")

    def test_within_range(self):
        self.assertIsNone(_check_duration(_video(300), 120, 7200))

    def test_exactly_at_min(self):
        self.assertIsNone(_check_duration(_video(120), 120, 7200))

    def test_exactly_at_max(self):
        self.assertIsNone(_check_duration(_video(7200), 120, 7200))

    def test_unknown_duration_passes(self):
        self.assertIsNone(_check_duration(_video(None), 120, 7200))


class TruncateTranscriptTest(unittest.TestCase):
    def test_truncates_long_text(self):
        t = _transcript("a" * 200)
        result = _truncate_transcript(t, max_chars=100)
        self.assertEqual(len(result.transcript_text), 100)

    def test_no_truncation_when_zero(self):
        t = _transcript("a" * 200)
        result = _truncate_transcript(t, max_chars=0)
        self.assertEqual(len(result.transcript_text), 200)

    def test_no_truncation_when_under_limit(self):
        t = _transcript("short")
        result = _truncate_transcript(t, max_chars=1000)
        self.assertIs(result, t)

    def test_segments_cleared_after_truncation(self):
        from models import TranscriptSegment
        t = _transcript("a" * 200)
        t = t.model_copy(update={"segments": [TranscriptSegment(text="hi", start=0.0, duration=1.0)]})
        result = _truncate_transcript(t, max_chars=50)
        self.assertEqual(result.segments, [])

    def test_original_not_mutated(self):
        t = _transcript("a" * 200)
        original_text = t.transcript_text
        _truncate_transcript(t, max_chars=50)
        self.assertEqual(t.transcript_text, original_text)


if __name__ == "__main__":
    unittest.main()
