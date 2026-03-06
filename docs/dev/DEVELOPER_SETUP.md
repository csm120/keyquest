# KeyQuest Developer Setup (Windows)

## Prerequisites

- Python 3 (with `python` and `pip` on PATH)
- Optional but recommended for accessibility dialogs: `wxPython`

## Install

1. Create and activate a virtual environment (recommended).
2. Install dependencies: `pip install -r requirements.txt`

## Run (from repo root)

- `python keyquest.pyw`

Notes:
- On Windows, screen reader support uses `cytolk` (Tolk). If it is not installed/available, KeyQuest falls back to `pyttsx3`.
- Current desktop accessibility research and product-direction notes are in `docs/dev/DESKTOP_ACCESSIBILITY_RESEARCH.md`.
- Lightweight manual verification steps are in `docs/dev/SCREEN_READER_SMOKE_TESTS.md`.
- The current accessibility direction is to preserve the custom speech-first Pygame experience and improve visual accessibility without reintroducing a heavy hybrid UI layer.

## Build / Package

- Build an `.exe` (PyInstaller): run `tools/build/build_exe.bat` (uses `tools/build/KeyQuest-RootFolders.spec`).
- Build a Windows installer (`.exe`): install Inno Setup 6, then run `tools/build/build_installer.bat` (uses `tools/build/installer/KeyQuest.iss` and outputs to `dist/installer/`).
- Create a source ZIP for sharing: run `tools/build/create_source_package.bat` (outputs to `source/`).
- Run a full release from `main` after bumping `modules/version.py`: `powershell -ExecutionPolicy Bypass -File tools/release.ps1`
  - Rebuilds `site/`
  - Runs tests by default
  - Rebuilds local `dist/` outputs by default
  - Refuses to publish unless `docs/user/WHATS_NEW.md` was updated for the release in plain language
  - Commits and pushes `main`
  - Creates and pushes the matching `v<version>` tag from `modules/version.py`
  - Triggers GitHub Pages and the GitHub Release workflow so the in-app updater can see the new version
  - Use `-DryRun` to verify the release steps without committing, pushing, or tagging
- Optional single entrypoint (logs to `tests/logs/`):
  - `powershell -ExecutionPolicy Bypass -File tools/build.ps1 -Target all -Clean` (exe + source)
  - `powershell -ExecutionPolicy Bypass -File tools/build.ps1 -Target installer` (installer only)

## Package Sanity Check

- `tools/build/create_source_package.bat` prints sample ZIP entries after building to confirm the folder structure is preserved.
