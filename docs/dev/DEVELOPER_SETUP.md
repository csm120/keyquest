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

## Build / Package

- Build an `.exe` (PyInstaller): run `tools/build/build_exe.bat` (uses `tools/build/KeyQuest-RootFolders.spec`).
- Build a Windows installer (`.exe`): install Inno Setup 6, then run `tools/build/build_installer.bat` (uses `tools/build/installer/KeyQuest.iss` and outputs to `dist/installer/`).
- Create a source ZIP for sharing: run `tools/build/create_source_package.bat` (outputs to `source/`).
- Optional single entrypoint (logs to `tests/logs/`):
  - `powershell -ExecutionPolicy Bypass -File tools/build.ps1 -Target all -Clean` (exe + source)
  - `powershell -ExecutionPolicy Bypass -File tools/build.ps1 -Target installer` (installer only)

## Package Sanity Check

- `tools/build/create_source_package.bat` prints sample ZIP entries after building to confirm the folder structure is preserved.
