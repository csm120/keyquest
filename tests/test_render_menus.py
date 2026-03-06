import unittest

from ui import render_menus


class TestRenderMenusHelpers(unittest.TestCase):
    def test_visible_window_returns_full_range_when_items_fit(self):
        self.assertEqual(render_menus.get_visible_window(5, 2, 8), (0, 5))

    def test_visible_window_keeps_current_item_in_view(self):
        start, end = render_menus.get_visible_window(21, 10, 7)
        self.assertLessEqual(start, 10)
        self.assertGreater(end, 10)
        self.assertEqual(end - start, 7)

    def test_visible_window_shifts_to_end_cleanly(self):
        self.assertEqual(render_menus.get_visible_window(21, 20, 7), (14, 21))


if __name__ == "__main__":
    unittest.main()
