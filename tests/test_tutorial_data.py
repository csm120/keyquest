import unittest


class TestTutorialData(unittest.TestCase):
    def test_tutorial_data_consistency(self):
        try:
            from modules import tutorial_data
        except Exception as e:  # pragma: no cover
            self.skipTest(f"tutorial_data import failed: {e}")

        all_names = [name for name, _key in tutorial_data.PHASE3_MIX_KEYS]
        self.assertTrue(all_names)

        for name in all_names:
            self.assertIn(name, tutorial_data.FRIENDLY)
            self.assertIn(name, tutorial_data.HINTS)

        self.assertGreater(tutorial_data.TUTORIAL_EACH_COUNT, 0)
        self.assertGreater(tutorial_data.TUTORIAL_MIX_COUNT, 0)

    def test_next_mode_from_performance(self):
        from modules import tutorial_data

        self.assertEqual(tutorial_data.next_mode_from_performance(0.95, 1), "fast")
        self.assertEqual(tutorial_data.next_mode_from_performance(0.70, 2), "slow")
        self.assertEqual(tutorial_data.next_mode_from_performance(0.82, 3), "normal")

    def test_build_phase_sequence_adds_extra_for_troublesome_keys(self):
        from modules import tutorial_data

        seq, targets = tutorial_data.build_phase_sequence(
            phase=5,
            mode="normal",
            key_errors={"space": 7, "enter": 0},
        )
        self.assertTrue(seq)
        self.assertGreater(targets["space"], targets["enter"])

    def test_intro_items_include_tactile_guidance(self):
        from modules import tutorial_data

        items = tutorial_data.get_intro_items_for_phase(2)
        self.assertTrue(items)
        names = [n for n, _ in items]
        self.assertIn("up", names)
        self.assertIn("down", names)


if __name__ == "__main__":
    unittest.main()
