import unittest

from ui import render_free_practice_ready


class TestFreePracticeReadyHelpers(unittest.TestCase):
    def test_visible_window_for_free_practice_uses_shared_helper(self):
        start, end = render_free_practice_ready.get_visible_window(12, 5, 6)
        self.assertLessEqual(start, 5)
        self.assertGreater(end, 5)
        self.assertEqual(end - start, 6)


if __name__ == "__main__":
    unittest.main()
