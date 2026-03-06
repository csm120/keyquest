# KeyQuest

KeyQuest is an accessible typing practice program for keyboard, screen reader, and low-vision users.

## For Users

Open [README.html](README.html) in a web browser for the plain-language guide.

Recent user-facing changes are tracked in [WHATS_NEW.md](docs/user/WHATS_NEW.md).

## For Contributors

Developer notes and session context live under [docs/dev](docs/dev).

- Start with [SESSION_START_GUIDE.md](docs/dev/SESSION_START_GUIDE.md)
- Current project context is in [HANDOFF.md](docs/dev/HANDOFF.md)
- Detailed project history is in [CHANGELOG.md](docs/dev/CHANGELOG.md)
- Desktop accessibility direction is in [DESKTOP_ACCESSIBILITY_RESEARCH.md](docs/dev/DESKTOP_ACCESSIBILITY_RESEARCH.md)
- Manual screen reader checks are in [SCREEN_READER_SMOKE_TESTS.md](docs/dev/SCREEN_READER_SMOKE_TESTS.md)
- For a full release that updates GitHub Pages, the installer, the portable ZIP, and the in-app updater target, run `powershell -ExecutionPolicy Bypass -File tools/release.ps1` after updating `modules/version.py` to a new version number.
  - Add `-DryRun` first if you want to verify the workflow without pushing or tagging.
  - The release script now refuses to publish unless `docs/user/WHATS_NEW.md` has been updated in plain language for that release.

## Contact

- Website: webfriendlyhelp.com
- Feedback: help@webfriendlyhelp.com
