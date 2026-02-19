import unittest
from datetime import date

from modules.state_manager import Settings
from modules import streak_manager


class TestStreakManager(unittest.TestCase):
    def test_first_time_sets_streak_and_date(self):
        settings = Settings()
        settings.last_practice_date = ""
        settings.current_streak = 0
        settings.longest_streak = 0

        milestone = streak_manager.check_and_update_streak(settings, today=date(2025, 12, 16))
        self.assertIsNone(milestone)
        self.assertEqual(settings.current_streak, 1)
        self.assertEqual(settings.last_practice_date, "2025-12-16")
        self.assertEqual(settings.longest_streak, 1)

    def test_same_day_no_change(self):
        settings = Settings()
        settings.last_practice_date = "2025-12-16"
        settings.current_streak = 5
        settings.longest_streak = 10

        milestone = streak_manager.check_and_update_streak(settings, today=date(2025, 12, 16))
        self.assertIsNone(milestone)
        self.assertEqual(settings.current_streak, 5)
        self.assertEqual(settings.last_practice_date, "2025-12-16")
        self.assertEqual(settings.longest_streak, 10)

    def test_consecutive_day_increments_and_returns_milestone(self):
        settings = Settings()
        settings.last_practice_date = "2025-12-15"
        settings.current_streak = 2
        settings.longest_streak = 2

        milestone = streak_manager.check_and_update_streak(settings, today=date(2025, 12, 16))
        self.assertEqual(milestone, 3)
        self.assertEqual(settings.current_streak, 3)
        self.assertEqual(settings.last_practice_date, "2025-12-16")
        self.assertEqual(settings.longest_streak, 3)

    def test_break_resets_to_one(self):
        settings = Settings()
        settings.last_practice_date = "2025-12-10"
        settings.current_streak = 8
        settings.longest_streak = 10

        milestone = streak_manager.check_and_update_streak(settings, today=date(2025, 12, 16))
        self.assertIsNone(milestone)
        self.assertEqual(settings.current_streak, 1)
        self.assertEqual(settings.last_practice_date, "2025-12-16")
        self.assertEqual(settings.longest_streak, 10)

    def test_invalid_last_date_resets_to_one(self):
        settings = Settings()
        settings.last_practice_date = "not-a-date"
        settings.current_streak = 9
        settings.longest_streak = 9

        milestone = streak_manager.check_and_update_streak(settings, today=date(2025, 12, 16))
        self.assertIsNone(milestone)
        self.assertEqual(settings.current_streak, 1)
        self.assertEqual(settings.last_practice_date, "2025-12-16")
        self.assertEqual(settings.longest_streak, 9)

    def test_get_streak_announcement(self):
        settings = Settings()
        settings.current_streak = 0
        self.assertEqual(streak_manager.get_streak_announcement(settings), "")

        settings.current_streak = 1
        self.assertEqual(streak_manager.get_streak_announcement(settings), "Day 1 of your streak!")

        settings.current_streak = 4
        self.assertEqual(streak_manager.get_streak_announcement(settings), "Day 4 streak! Keep going!")


if __name__ == "__main__":
    unittest.main()

