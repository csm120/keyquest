import unittest

from modules import pet_manager
from modules import state_manager


class TestPetSessionProgress(unittest.TestCase):
    def test_apply_session_pet_progress_no_pet(self):
        settings = state_manager.Settings()
        result = pet_manager.apply_session_pet_progress(
            settings,
            recent_performance={"accuracy": 90, "session_duration": 5},
            xp_amount=25,
        )
        self.assertFalse(result["has_pet"])

    def test_apply_session_pet_progress_awards_xp_and_evolves(self):
        settings = state_manager.Settings()
        pet_manager.choose_pet(settings, "robot")
        settings.pet_xp = 490

        result = pet_manager.apply_session_pet_progress(
            settings,
            recent_performance={
                "new_best_wpm": True,
                "new_best_accuracy": False,
                "accuracy": 96,
                "session_duration": 12,
                "streak_broken": False,
            },
            xp_amount=20,
        )

        self.assertTrue(result["has_pet"])
        self.assertTrue(result["evolved"])
        self.assertEqual(result["new_stage"], 2)
        self.assertEqual(settings.pet_xp, 510)

    def test_apply_session_pet_progress_updates_mood(self):
        settings = state_manager.Settings()
        pet_manager.choose_pet(settings, "owl")

        result = pet_manager.apply_session_pet_progress(
            settings,
            recent_performance={
                "new_best_wpm": False,
                "new_best_accuracy": False,
                "accuracy": 82,
                "session_duration": 35,
                "streak_broken": False,
            },
            xp_amount=10,
        )

        self.assertEqual(result["mood"], "tired")
        self.assertEqual(settings.pet_mood, "tired")
        self.assertEqual(settings.pet_happiness, 49)
        self.assertTrue(result["mood_message"])


if __name__ == "__main__":
    unittest.main()
