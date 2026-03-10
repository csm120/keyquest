import unittest
from unittest import mock

from modules import error_logging


class TestErrorLogging(unittest.TestCase):
    def test_copy_log_to_clipboard_uses_full_log_contents(self):
        with mock.patch("modules.error_logging.read_full_log", return_value="sample log text"):
            with mock.patch("modules.error_logging.copy_text_to_clipboard", return_value=True) as copy_mock:
                copied = error_logging.copy_log_to_clipboard()

        self.assertTrue(copied)
        copy_mock.assert_called_once_with("sample log text")

    def test_copy_log_to_clipboard_returns_false_for_empty_log(self):
        with mock.patch("modules.error_logging.read_full_log", return_value=""):
            with mock.patch("modules.error_logging.copy_text_to_clipboard") as copy_mock:
                copied = error_logging.copy_log_to_clipboard()

        self.assertFalse(copied)
        copy_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
