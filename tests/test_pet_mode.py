from types import SimpleNamespace
import unittest

from modules import pet_mode
from modules import pet_ui_data


class TestPetMode(unittest.TestCase):
    def test_ensure_pet_ui_state_populates_missing_attributes(self):
        app = SimpleNamespace()

        pet_mode.ensure_pet_ui_state(app)

        self.assertEqual(app.pet_options, list(pet_ui_data.PET_MENU_OPTIONS))
        self.assertEqual(app.pet_types, [])
        self.assertEqual(app.pet_view, "status")
        self.assertEqual(app.pet_menu_index, 0)
        self.assertEqual(app.pet_choose_index, 0)
        self.assertEqual(app.pet_choose_mode, "new")

    def test_ensure_pet_ui_state_preserves_existing_attributes(self):
        app = SimpleNamespace(
            pet_options=["Custom"],
            pet_types=["owl"],
            pet_view="choose",
            pet_menu_index=2,
            pet_choose_index=1,
            pet_choose_mode="change",
        )

        pet_mode.ensure_pet_ui_state(app)

        self.assertEqual(app.pet_options, ["Custom"])
        self.assertEqual(app.pet_types, ["owl"])
        self.assertEqual(app.pet_view, "choose")
        self.assertEqual(app.pet_menu_index, 2)
        self.assertEqual(app.pet_choose_index, 1)
        self.assertEqual(app.pet_choose_mode, "change")


if __name__ == "__main__":
    unittest.main()
