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
- To ship a full release with an automatic version-bump suggestion, run `powershell -ExecutionPolicy Bypass -File tools/ship_updates.ps1`.
  - Add `-Bump patch` or `-Bump minor` if you want to choose the bump yourself.
  - Add `-DryRun` first if you want to verify the workflow without pushing or tagging.
- `tools/release.ps1` is still available if you want to bump `modules/version.py` manually before releasing.
  - The release flow refuses to publish unless `docs/user/WHATS_NEW.md` has been updated in plain language for that release.

## Contact

- Website: webfriendlyhelp.com
- Feedback: help@webfriendlyhelp.com
