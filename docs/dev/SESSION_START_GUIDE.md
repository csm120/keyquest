# Quick Start Guide for New Sessions

**Last Updated:** 2026-02-14

## For the User

Tell the assistant: **"Read docs/dev/HANDOFF.md"**.

## For the Assistant

1. Read `docs/dev/HANDOFF.md` first.
2. Read the top entry in `docs/user/CHANGELOG.md`.
3. Read additional docs only if the task needs them.

## Current Project Status

- Accessibility documentation is available under `docs/user/`.
- Core features are implemented (tutorial, lessons, practice, tests, games, badges, XP, quests, daily challenges, shop, pets).
- Root/build cleanup complete:
  - Build scripts/spec under `tools/build/`
  - Quality script under `tools/quality/`
  - Developer setup doc at `docs/dev/DEVELOPER_SETUP.md`

## Key Files

- Entrypoint: `keyquest.pyw`
- Main app: `modules/keyquest_app.py`
- Modules: `modules/*.py`
- Games: `games/*.py`
- UI renderers: `ui/*.py`
- Tests: `tests/test_*.py`

## Common Commands

- Run app: `python keyquest.pyw`
- Run tests: `python -m unittest`
- Quality checks: `powershell -ExecutionPolicy Bypass -File tools/run_quality_checks.ps1`
- Build exe: `tools/build/build_exe.bat`
- Build source zip: `tools/build/create_source_package.bat`
- Full build: `powershell -ExecutionPolicy Bypass -File tools/build.ps1 -Target all -Clean`

## Conventions

- Keep speech and visual text aligned.
- Use `priority=True` + `protect_seconds` for important announcements.
- Update `docs/user/CHANGELOG.md` and `docs/dev/HANDOFF.md` for meaningful behavior changes.
- Prefer updating existing docs instead of creating new one-off markdown files.
