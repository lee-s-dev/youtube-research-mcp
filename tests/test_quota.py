import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import cache


class QuotaLogTest(unittest.TestCase):
    def test_log_and_retrieve_today(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict("os.environ", {"YOUTUBE_RESEARCH_CACHE_DB": str(Path(tmpdir) / "cache.db")}):
                cache.log_quota("search.list", 100)
                cache.log_quota("videos.list", 1)
                cache.log_quota("commentThreads.list", 1)

                result = cache.get_quota_today()

                self.assertEqual(result["total_units_used"], 102)
                self.assertEqual(result["daily_limit"], 10000)
                self.assertEqual(result["remaining_estimate"], 9898)
                self.assertEqual(result["breakdown"]["search.list"], 100)
                self.assertEqual(result["breakdown"]["videos.list"], 1)

    def test_quota_empty_day(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict("os.environ", {"YOUTUBE_RESEARCH_CACHE_DB": str(Path(tmpdir) / "cache.db")}):
                result = cache.get_quota_today()
                self.assertEqual(result["total_units_used"], 0)
                self.assertEqual(result["remaining_estimate"], 10000)
                self.assertEqual(result["breakdown"], {})

    def test_multiple_same_operation_sums(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict("os.environ", {"YOUTUBE_RESEARCH_CACHE_DB": str(Path(tmpdir) / "cache.db")}):
                cache.log_quota("search.list", 100)
                cache.log_quota("search.list", 100)
                cache.log_quota("search.list", 100)

                result = cache.get_quota_today()
                self.assertEqual(result["breakdown"]["search.list"], 300)


if __name__ == "__main__":
    unittest.main()
