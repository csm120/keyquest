import tempfile
import unittest
from pathlib import Path
from unittest import mock

from modules import update_manager


class TestUpdateManager(unittest.TestCase):
    def test_normalize_version_handles_v_prefix(self):
        self.assertEqual(update_manager.normalize_version("v1.2.3"), "1.2.3")

    def test_is_newer_version_compares_numeric_parts(self):
        self.assertTrue(update_manager.is_newer_version("1.0", "1.0.1"))
        self.assertFalse(update_manager.is_newer_version("1.2.0", "1.2"))

    def test_select_installer_asset_prefers_exact_setup_name(self):
        release = {
            "assets": [
                {"name": "something-else.exe", "browser_download_url": "https://example.invalid/other.exe"},
                {"name": "KeyQuestSetup.exe", "browser_download_url": "https://example.invalid/KeyQuestSetup.exe"},
            ]
        }
        asset = update_manager.select_installer_asset(release)
        self.assertIsNotNone(asset)
        self.assertEqual(asset["name"], "KeyQuestSetup.exe")

    def test_select_portable_asset_prefers_expected_zip_name(self):
        release = {
            "assets": [
                {"name": "KeyQuest-portable.zip", "browser_download_url": "https://example.invalid/portable.zip"},
                {"name": "KeyQuest-win64.zip", "browser_download_url": "https://example.invalid/KeyQuest-win64.zip"},
            ]
        }
        asset = update_manager.select_portable_asset(release)
        self.assertIsNotNone(asset)
        self.assertEqual(asset["name"], "KeyQuest-win64.zip")

    def test_parse_release_version_uses_tag_name(self):
        release = {"tag_name": "v1.4.2"}
        self.assertEqual(update_manager.parse_release_version(release), "1.4.2")

    def test_build_ssl_context_uses_default_store_and_loads_certifi_bundle(self):
        fake_context = mock.Mock()
        fake_certifi = mock.Mock()
        fake_certifi.where.return_value = "C:\\certifi\\cacert.pem"

        with mock.patch("modules.update_manager.ssl.create_default_context", return_value=fake_context):
            with mock.patch.object(update_manager, "certifi", fake_certifi):
                context = update_manager._build_ssl_context()

        self.assertIs(context, fake_context)
        fake_context.load_verify_locations.assert_called_once_with(cafile="C:\\certifi\\cacert.pem")

    def test_create_update_launcher_contains_silent_install_and_restart(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            installer = Path(tmpdir) / "KeyQuestSetup_1_2_0.exe"
            script = update_manager.create_update_launcher(
                installer_path=installer,
                app_dir=r"C:\Users\Test\AppData\Local\Programs\KeyQuest",
                app_exe_path=r"C:\Program Files\KeyQuest\KeyQuest.exe",
                current_pid=1234,
                script_path=Path(tmpdir) / "update.cmd",
            )
            content = script.read_text(encoding="utf-8")

        self.assertIn("/VERYSILENT", content)
        self.assertIn("/NOCANCEL", content)
        self.assertIn('BACKUP_DIR', content)
        self.assertIn('progress.json', content)
        self.assertIn('Get-Content -LiteralPath $_.FullName', content)
        self.assertIn('Get-Content -LiteralPath $dest', content)
        self.assertIn('Set-Content -LiteralPath $dest -Value $merged', content)
        self.assertIn('start "" "%APP_EXE%"', content)
        self.assertIn('set "TARGET_PID=1234"', content)

    def test_create_portable_update_launcher_contains_expand_and_robocopy(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            portable_zip = Path(tmpdir) / "KeyQuest-win64_1_2_0.zip"
            script = update_manager.create_portable_update_launcher(
                zip_path=portable_zip,
                app_dir=r"C:\Portable\KeyQuest",
                app_exe_path=r"C:\Portable\KeyQuest\KeyQuest.exe",
                current_pid=5678,
                script_path=Path(tmpdir) / "portable-update.cmd",
            )
            content = script.read_text(encoding="utf-8")

        self.assertIn("Expand-Archive", content)
        self.assertIn("releaseSentences", content)
        self.assertIn('Get-Content -LiteralPath $_.FullName', content)
        self.assertIn('Get-Content -LiteralPath $dest', content)
        self.assertIn('Set-Content -LiteralPath $dest -Value $merged', content)
        self.assertIn("robocopy", content)
        self.assertIn("/XF progress.json", content)
        self.assertIn('set "TARGET_PID=5678"', content)

    def test_is_portable_layout_detects_extracted_app_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "KeyQuest.exe").write_text("", encoding="utf-8")
            (root / "modules").mkdir()
            (root / "games").mkdir()
            (root / "Sentences").mkdir()

            self.assertTrue(update_manager.is_portable_layout(str(root)))


if __name__ == "__main__":
    unittest.main()
