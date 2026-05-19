import unittest

from server import dedupe_video_ids


class ServerHelpersTest(unittest.TestCase):
    def test_dedupe_video_ids_preserves_order(self):
        self.assertEqual(
            dedupe_video_ids(
                [
                    "https://youtu.be/tTw1z10yMCI",
                    "tTw1z10yMCI",
                    "https://www.youtube.com/watch?v=RhTiAOGwbYE",
                ]
            ),
            ["tTw1z10yMCI", "RhTiAOGwbYE"],
        )

    def test_dedupe_video_ids_requires_input(self):
        with self.assertRaises(ValueError):
            dedupe_video_ids([])


if __name__ == "__main__":
    unittest.main()
