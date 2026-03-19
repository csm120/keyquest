import importlib.util
import pathlib
import unittest


SCRIPT_PATH = pathlib.Path(__file__).resolve().parents[1] / "tools" / "dev" / "release_bump.py"
SPEC = importlib.util.spec_from_file_location("release_bump", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class TestReleaseBump(unittest.TestCase):
    def test_sync_readme_version_text_updates_guide_and_about_version(self):
        source = (
            "<p><strong>Version {{APP_VERSION}}</strong></p>\n"
            "<li><strong>Application</strong>: KeyQuest {{APP_VERSION}}</li>\n"
        )
        updated = MODULE.sync_readme_version_text(source, "2.0.1")
        self.assertIn("Version 2.0.1", updated)
        self.assertIn("Application</strong>: KeyQuest 2.0.1", updated)

    def test_sync_whats_new_version_text_updates_first_visible_version_only(self):
        source = (
            "# New in Key Quest\n\n"
            "## Friday March 20th 2026\n\n"
            "Version 1.3.0\n\n"
            "Notes.\n\n"
            "Version 1.2.9\n"
        )
        updated = MODULE.sync_whats_new_version_text(source, "1.3.1")
        self.assertIn("Version 1.3.1", updated)
        self.assertIn("Version 1.2.9", updated)


if __name__ == "__main__":
    unittest.main()
