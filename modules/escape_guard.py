"""Escape key press guard utilities."""

from typing import Tuple


class EscapePressGuard:
    """Track repeated Escape presses within a changing UI context."""

    def __init__(self):
        self._count = 0
        self._context = ""

    def reset(self) -> None:
        self._count = 0
        self._context = ""

    def register_escape(self, context: str, required_presses: int = 3) -> Tuple[bool, int]:
        """Record an Escape key press.

        Returns:
            (completed, remaining_presses)
        """
        required = max(1, int(required_presses))
        if self._context != context:
            self._context = context
            self._count = 0

        self._count += 1
        remaining = required - self._count
        if remaining <= 0:
            self.reset()
            return True, 0
        return False, remaining
