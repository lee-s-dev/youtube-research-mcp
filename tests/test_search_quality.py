import unittest

from models import SearchResult
from youtube_utils import filter_search_quality


def _result(video_id, *, duration=None, view_count=None, channel=None, title=None):
    return SearchResult(
        video_id=video_id,
        url=f"https://www.youtube.com/watch?v={video_id}",
        duration_seconds=duration,
        view_count=view_count,
        channel_name=channel,
        title=title,
    )


class FilterSearchQualityTest(unittest.TestCase):
    def test_excludes_shorts_by_duration(self):
        results = [
            _result("aaaaaaaaaaa", duration=60),
            _result("bbbbbbbbbbb", duration=91),
            _result("ccccccccccc", duration=90),
        ]
        filtered = filter_search_quality(results, exclude_shorts=True)
        self.assertEqual([r.video_id for r in filtered], ["bbbbbbbbbbb"])

    def test_excludes_shorts_by_title_hashtag(self):
        results = [
            _result("aaaaaaaaaaa", title="Cool video #Shorts"),
            _result("bbbbbbbbbbb", title="Full tutorial"),
        ]
        filtered = filter_search_quality(results, exclude_shorts=True)
        self.assertEqual([r.video_id for r in filtered], ["bbbbbbbbbbb"])

    def test_keeps_shorts_when_disabled(self):
        results = [_result("aaaaaaaaaaa", duration=30)]
        filtered = filter_search_quality(results, exclude_shorts=False)
        self.assertEqual(len(filtered), 1)

    def test_passes_unknown_duration_when_excluding_shorts(self):
        results = [_result("aaaaaaaaaaa", duration=None)]
        filtered = filter_search_quality(results, exclude_shorts=True)
        self.assertEqual(len(filtered), 1)

    def test_min_view_count(self):
        results = [
            _result("aaaaaaaaaaa", view_count=500),
            _result("bbbbbbbbbbb", view_count=5000),
            _result("ccccccccccc", view_count=None),
        ]
        filtered = filter_search_quality(results, exclude_shorts=False, min_view_count=1000)
        self.assertEqual([r.video_id for r in filtered], ["bbbbbbbbbbb"])

    def test_min_view_count_zero_disables_filter(self):
        results = [_result("aaaaaaaaaaa", view_count=1)]
        filtered = filter_search_quality(results, exclude_shorts=False, min_view_count=0)
        self.assertEqual(len(filtered), 1)

    def test_max_per_channel(self):
        results = [
            _result("aaaaaaaaaaa", channel="Chan A"),
            _result("bbbbbbbbbbb", channel="Chan A"),
            _result("ccccccccccc", channel="Chan B"),
        ]
        filtered = filter_search_quality(results, exclude_shorts=False, max_per_channel=1)
        self.assertEqual(len(filtered), 2)
        channels = [r.channel_name for r in filtered]
        self.assertIn("Chan A", channels)
        self.assertIn("Chan B", channels)

    def test_max_per_channel_zero_disables_limit(self):
        results = [
            _result("aaaaaaaaaaa", channel="Chan A"),
            _result("bbbbbbbbbbb", channel="Chan A"),
        ]
        filtered = filter_search_quality(results, exclude_shorts=False, max_per_channel=0)
        self.assertEqual(len(filtered), 2)

    def test_combined_filters(self):
        results = [
            _result("aaaaaaaaaaa", duration=60, view_count=10000, channel="A"),
            _result("bbbbbbbbbbb", duration=300, view_count=100, channel="A"),
            _result("ccccccccccc", duration=300, view_count=10000, channel="A"),
            _result("ddddddddddd", duration=300, view_count=10000, channel="B"),
        ]
        filtered = filter_search_quality(
            results, exclude_shorts=True, min_view_count=1000, max_per_channel=1
        )
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0].video_id, "ccccccccccc")
        self.assertEqual(filtered[1].video_id, "ddddddddddd")


if __name__ == "__main__":
    unittest.main()
