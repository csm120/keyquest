import unittest

from ui import layout


class _FakeScreen:
    def __init__(self, size):
        self._size = size

    def get_size(self):
        return self._size


class TestLayoutHelpers(unittest.TestCase):
    def test_get_screen_size_uses_fallback_without_surface(self):
        self.assertEqual(layout.get_screen_size(None), (900, 600))

    def test_get_screen_size_reads_live_surface_size(self):
        self.assertEqual(layout.get_screen_size(_FakeScreen((1280, 720))), (1280, 720))

    def test_get_content_width_respects_margin_and_max_width(self):
        self.assertEqual(layout.get_content_width(1000, side_margin=80, max_width=700), 700)
        self.assertEqual(layout.get_content_width(500, side_margin=80, max_width=700), 340)

    def test_get_footer_y_applies_padding(self):
        self.assertEqual(layout.get_footer_y(600), 570)
        self.assertEqual(layout.get_footer_y(600, padding=50), 550)


if __name__ == "__main__":
    unittest.main()
