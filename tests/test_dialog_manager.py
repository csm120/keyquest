import unittest
from unittest.mock import Mock, patch

from modules import dialog_manager


class TestDialogManager(unittest.TestCase):
    def test_restore_pygame_focus_restores_windows_window(self):
        fake_pygame = Mock()
        fake_pygame.display.get_init.return_value = True
        fake_pygame.display.get_wm_info.return_value = {"window": 1234}

        user32 = Mock()
        windll = Mock(user32=user32)

        with patch.object(dialog_manager, "PYGAME_AVAILABLE", True), \
             patch.object(dialog_manager, "pygame", fake_pygame), \
             patch.object(dialog_manager.sys, "platform", "win32"), \
             patch("ctypes.windll", windll, create=True):
            dialog_manager.restore_pygame_focus()

        fake_pygame.event.clear.assert_called_once()
        fake_pygame.event.pump.assert_called_once()
        user32.ShowWindow.assert_called_once_with(1234, 9)
        user32.SetForegroundWindow.assert_called_once_with(1234)
        user32.SetActiveWindow.assert_called_once_with(1234)
        user32.SetFocus.assert_called_once_with(1234)

    def test_restore_pygame_focus_skips_window_calls_off_windows(self):
        fake_pygame = Mock()

        with patch.object(dialog_manager, "PYGAME_AVAILABLE", True), \
             patch.object(dialog_manager, "pygame", fake_pygame), \
             patch.object(dialog_manager.sys, "platform", "linux"):
            dialog_manager.restore_pygame_focus()

        fake_pygame.event.clear.assert_called_once()
        fake_pygame.event.pump.assert_called_once()
        fake_pygame.display.get_init.assert_not_called()


if __name__ == "__main__":
    unittest.main()
