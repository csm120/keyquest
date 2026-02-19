# KeyQuest Handoff (Canonical Context)

This is the single starting point for any human or AI working on KeyQuest.

## Snapshot

- **Last updated**: 2026-02-19 (Version 1.0 published to GitHub + release assets uploaded)
- **Version**: 1.0 (source of truth: `modules/version.py`)
- **Platform**: Windows (full accessibility) / Linux (TTS only)
- **Accessibility**: See user accessibility docs in `docs/user/`.

## Next Session Checklist

1. Open `docs/dev/HANDOFF.md` and `docs/user/CHANGELOG.md` top entry.
2. Run baseline checks before editing:
   - `python -m unittest`
   - `powershell -ExecutionPolicy Bypass -File tools/run_quality_checks.ps1`
3. If changing user-visible behavior, update:
   - `README.html` (and pointer `README.md` only if needed)
   - `docs/user/CHANGELOG.md`
4. For release work:
   - Build exe: `cmd /c tools\build\build_exe.bat --nopause`
   - Build installer: `cmd /c tools\build\build_installer.bat --nopause`
   - Verify release assets in `dist/`
5. Before handoff:
   - Update this handoff file snapshot + recent changes
   - Commit and push to `main`
   - If releasing, verify GitHub release page and asset links

## Quick Start (For New Sessions)

1. Read this file.
2. Read the top entry in `docs/user/CHANGELOG.md`.
3. Start implementation from `modules/keyquest_app.py` and the relevant `modules/*` or `games/*` file.

## Repo Map (Where Things Live)

- `keyquest.pyw`: thin entrypoint (runs `modules/keyquest_app.py`).
- `modules/keyquest_app.py`: main application event loop and screen wiring.
- `modules/`: state, lessons, audio, dialogs, menu, shop/pets, etc.
- `games/`: game implementations (`base_game.py`, `letter_fall.py`, `word_typing.py`).
- `ui/`: rendering helpers.
- `Sentences/`: sentence/topic text pools.
- `docs/`: user and developer docs.
- `tools/build/`: batch build scripts and PyInstaller spec.
- `tools/quality/`: quality scripts (contrast audit).

## Run / Test / Build

- Install deps: `pip install -r requirements.txt`
- Run app: `python keyquest.pyw`
- Run tests: `python -m unittest`
- Local quality checks: `powershell -ExecutionPolicy Bypass -File tools/run_quality_checks.ps1`
- Build exe: `tools/build/build_exe.bat`
- Build installer: `tools/build/build_installer.bat` (requires Inno Setup 6)
- Build source package: `tools/build/create_source_package.bat`
- Single build entrypoint:
  - `powershell -ExecutionPolicy Bypass -File tools/build.ps1 -Target all -Clean` (exe + source)
  - `powershell -ExecutionPolicy Bypass -File tools/build.ps1 -Target installer` (installer only)
- EXE packaging docs policy: include `README.md`, `README.html`, and `CHANGELOG.md` under `dist/KeyQuest/docs/`.

## Current Status (High Level)

- Core app + Phases 1-4 features implemented.
- New user-facing guide is now `README.html` (plain-language, WCAG-friendly structure). `README.md` is a pointer.
- Hangman is fully integrated and significantly expanded:
  - offline dictionary-backed words/definitions
  - weighted word-length selection centered on common lengths, with occasional short and very long words
  - 10 wrong-guess visual stages with spoken stage descriptions
  - comma-separated spoken word progress tokens for clearer SR pacing
  - Left/Right/Home/End cursor navigation across word-progress positions with visual focus highlight
  - results menu with `Word`, `Definition`, copy action, replay, and sentence-practice bridge
  - sentence-practice prompts use varied style templates (story/mystery/science/etc.) instead of plain repetitive lines
  - sentence-practice `Ctrl+Space` reads remaining text from current typing position
  - `Alt+L` reports letters left and total letters
- Speech formatting is now consistent for repeated letters/spaces and mismatch feedback.
- Typing prompts now use clearer sequence wording for repeated/special-key patterns (e.g., "Type a, then space, then a").
- Early lessons (stages 0-5) now favor memory-friendly 3-4 key targets.
- Sentence Practice `Random Topic` excludes Spanish topics; Spanish is still available via `Choose Topic`.
- `Escape x3` return to Main Menu is implemented across active non-menu modes.
  - Escape handling is centralized via `modules/escape_guard.py` + policy routing in `modules/keyquest_app.py`.
- Main menu labels/order updated (`Quests`, `Pets`, `Pet Shop`, `Badges`).
- Main menu now includes `About` (menu-driven info screen with website launch action).
- Word Typing countdown stutter at 10s/5s fixed.
- Startup speech ordering stabilized (title first via SR, then first menu item).
- Fixed slow first down-arrow announcement caused by startup speech protection window.
- Added fixed 250 ms duplicate-speech debounce to reduce stutter/repeats.
- Added spoken/visual goodbye message on app exit.

## Active TODOs / Open Issues

1. Continue modularization of `modules/keyquest_app.py` where practical.
2. Keep docs in sync with active file layout under `tools/build/` and `tools/quality/`.
3. Add more focused behavior tests for speech/menu/game edge cases as needed.

## Key Conventions

- Use `self.speech.say("...", priority=True, protect_seconds=2.0)` for important announcements.
- Keep visual and spoken content aligned.
- Use `get_app_dir()` for runtime-safe path resolution (source and frozen exe).
- Update `docs/user/CHANGELOG.md` for user-visible behavior changes.

## Recent Changes

### 2026-02-19: Version 1.0 Release + About Screen

- Declared milestone release as `Version 1.0` (`modules/version.py`).
- Added `About: A` to the bottom of the main menu (`modules/state_manager.py`).
- Added new `ABOUT` mode in `modules/keyquest_app.py`:
  - menu-driven about items (app/version, name, company, tagline, copyright, license, website, credits, back)
  - website item opens `https://webfriendlyhelp.com` via default browser on Enter/Space
  - Escape returns to Main Menu
- Added `LICENSE` file with MIT terms for open collaboration and redistribution.
- Added Windows installer build path with Inno Setup:
  - `tools/build/installer/KeyQuest.iss`
  - `tools/build/build_installer.bat`
  - `tools/build.ps1 -Target installer`
- Updated `README.html` main menu docs with About details and Version 1.0 marker.

### 2026-02-19: GitHub Publish + Release Assets + README Contact Link

- Initialized git repo in workspace and published source to GitHub:
  - Repo: `https://github.com/csm120/KeyQuest`
  - Default branch: `main`
- Created and published release tag `v1.0` with downloadable assets:
  - `KeyQuestSetup-1.0.exe`
  - `KeyQuest-1.0-win64.zip`
  - Release page: `https://github.com/csm120/KeyQuest/releases/tag/v1.0`
- Updated README feedback links to include email subject:
  - `mailto:help@webfriendlyhelp.com?subject=KeyQuest%20Feedback`
- Removed dedicated Hangman item from the user-facing Games list in `README.html` while keeping Hangman implemented in app.
- Performed a source-comment wording pass for public-facing clarity in a few modules (`dialog_manager`, `currency_manager`, `key_analytics`, `lesson_manager`, `ui/pet_visuals`).

### 2026-02-19: Hangman UX + Escape Handler Unification

- Added shared escape press tracker: `modules/escape_guard.py`.
- Moved active-mode Escape behavior to centralized policy/handler in `modules/keyquest_app.py`.
  - Keyboard Explorer uses `Escape x3` via the shared path.
  - Sentence Practice finish-on-Escape-x3 now routes through the same centralized handler.
- `games/hangman.py` updates:
  - Word progress speech now uses comma separators (`c, blank, t`) for better SR clarity.
  - Added word-position cursor navigation (`Left/Right/Home/End`) with spoken position feedback and visual focus highlight.
  - Sentence-practice `Ctrl+Space` now announces remaining text based on current typing position.
  - Replaced simple sentence-practice templates with randomized style-based prompts for higher-quality, less repetitive lines.
  - Removed fixed max word length; max is now derived from dictionary data.
  - Updated word selection to favor common lengths while still allowing short and rare very long words.
- Documentation:
  - Updated `README.html` Hangman controls/details.
  - Updated `docs/user/CHANGELOG.md` with this change set.

### 2026-02-18: User Guide HTML + Packaging + Escape/Hotkey Doc Alignment

- Documentation:
  - Replaced user-facing readme content with `README.html` (plain-language, main-menu organized).
  - Added WCAG-oriented page structure for the guide (landmarks, skip link, focus-visible styles).
  - Simplified `README.md` to a pointer to `README.html`.
  - Updated `docs/user/CHANGELOG.md` with latest Hangman/readme/build notes.
- Build/distribution:
  - Updated `tools/build/KeyQuest-RootFolders.spec` to copy `README.html` to:
    - `dist/KeyQuest/README.html`
    - `dist/KeyQuest/docs/README.html`
- In-app docs text alignment:
  - Updated gameplay hotkey/instruction text for `Letter Fall`, `Word Typing`, and `Hangman` to reflect `Escape x3` exit behavior.

### 2026-02-16: Prompt Clarity + Early Lesson Sequence Length + Random Topic Rule

- `modules/speech_format.py`:
  - Added `spell_text_for_typing_instruction()` for clearer `Type ...` prompts.
  - Uses `then` separators when sequence order is likely important (special keys/spaces or repeated characters).
- `modules/lesson_mode.py`, `modules/keyquest_app.py`, `modules/lesson_manager.py`:
  - Unified typing-prompt formatting on the new helper.
  - Kept mismatch/remaining feedback format unchanged (`Missing: ... Remaining text: ...`).
- `modules/lesson_mode.py`:
  - Early stages (0-5) now normalize practice targets to 3-4 keys for easier recall.
- `modules/test_modes.py`:
  - `Random Topic` now picks from non-Spanish topics only (fallback to all topics if needed).
- Tests:
  - Updated/added coverage in `tests/test_speech_format.py`, `tests/test_lesson_mode.py`, and `tests/test_test_modes.py`.
- Docs:
  - Updated `README.md` and `docs/user/CHANGELOG.md` to match implemented behavior.

### 2026-02-14: Accessibility + Structure Follow-Through

- Added shared speech-format helpers and consistent mismatch announcements.
- Updated menu labels/order and Word Typing countdown behavior.
- Reorganized root helper/build files into `tools/build/`, `tools/quality/`, and `docs/`.
- Added targeted regression tests in `tests/test_test_modes.py` and `tests/test_word_typing.py`.
- Added adaptive tutorial flow (space-first onboarding, phase pacing based on performance, extra reps for troublesome keys).
- Added typing sound intensity option (`subtle` / `normal` / `strong`) with persistence.
- Updated PyInstaller spec for reorganized repo layout and stabilized Python 3.9 compatibility.
- Updated exe distribution docs policy to include only `README.md` and `CHANGELOG.md` in `dist/KeyQuest/docs/`.

### 2026-02-14: Startup Speech and Exit UX Follow-Up

- `modules/keyquest_app.py`:
  - Startup menu announcement is timer-driven to avoid racing with screen-reader title announcement.
  - Startup announcement uses non-interrupting speech for first menu item.
  - Removed startup priority protection that delayed first menu arrow navigation speech.
  - Quit path now shows and speaks a brief goodbye message before exiting.
- `modules/speech_manager.py`:
  - Added fixed duplicate-speech debounce (`0.25s`) for identical rapid repeats.

For full details, see the top entry in `docs/user/CHANGELOG.md`.
