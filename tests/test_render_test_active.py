import unittest

from ui import render_test_active


class _FakeSurface:
    def __init__(self, width):
        self._width = width
        self._height = 24

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def get_rect(self, topleft):
        import pygame

        return pygame.Rect(topleft[0], topleft[1], self._width, self._height)


class _FakeFont:
    def render(self, text, color):
        return _FakeSurface(max(20, len(text) * 10)), None


class TestRenderTestActiveHelpers(unittest.TestCase):
    def test_build_wrapped_lines_wraps_long_text(self):
        font = _FakeFont()
        lines = render_test_active._build_wrapped_lines(
            font,
            "one two three four five six",
            100,
            (255, 255, 255),
        )
        self.assertGreater(len(lines), 1)

    def test_build_wrapped_lines_uses_placeholder_for_empty_typed_text(self):
        font = _FakeFont()
        lines = render_test_active._build_wrapped_lines(
            font,
            "",
            200,
            (255, 255, 255),
        )
        self.assertEqual(lines, ["_"])


if __name__ == "__main__":
    unittest.main()
