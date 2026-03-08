"""Flash overlay state for visual keystroke feedback.

Tracks a brief full-screen color flash (green = correct, red = error)
that gives deaf/HoH users a visual equivalent of the audio beep feedback.
"""

import time


class FlashState:
    """Holds the color and expiry time for the current keystroke flash."""

    def __init__(self):
        self.color: tuple = (0, 0, 0)
        self.until: float = 0.0

    def trigger(self, color: tuple, duration: float = 0.12) -> None:
        """Schedule a flash overlay for the given color and duration (seconds)."""
        self.color = color
        self.until = time.time() + duration

    def is_active(self) -> bool:
        """Return True if a flash is currently visible."""
        return self.until > time.time()

    def current_alpha(self) -> int:
        """Return the current overlay alpha (0-60), fading as the flash expires."""
        if not self.is_active():
            return 0
        elapsed = self.until - time.time()
        return int(min(60, elapsed * 500))
