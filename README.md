# KeyQuest

[![Latest Release](https://img.shields.io/github/v/release/csm120/KeyQuest)](https://github.com/csm120/KeyQuest/releases/latest)

KeyQuest is an accessible typing adventure game for Windows, built with Python and designed for keyboard, screen reader, and low-vision users.

It focuses on players who want stronger non-visual support than most game projects provide, including clear spoken feedback, keyboard-first navigation, and packaged documentation for both web and desktop reading.

Download the latest installer or portable ZIP from the [Releases page](https://github.com/csm120/KeyQuest/releases), or browse the user guide on the [project website](https://csm120.github.io/KeyQuest/).

## Why KeyQuest

- Accessible-first design for screen reader, keyboard-only, and low-vision users
- Typing practice delivered through game structure instead of drills alone
- Windows releases available as both installer and portable ZIP
- Expandable game and sentence content stored in plain project folders

**Quick start** (requires Python 3.9):

```
pip install -r requirements.txt
py -3.9 keyquest.pyw
```

## For Users

Start with the [project website](https://csm120.github.io/KeyQuest/) or open [README.html](README.html) in a web browser for the plain-language guide.

Recent user-facing changes are tracked in [WHATS_NEW.md](docs/user/WHATS_NEW.md).

Key audience:

- Learners who want a more game-like way to practice typing
- Screen reader users who need reliable spoken feedback
- Low-vision and keyboard-only users who benefit from consistent navigation patterns

Current keyboard navigation highlights:

- `Home` jumps to the first item and `End` jumps to the last item in menus, lesson lists, options, and post-session choice menus.
- After lessons and Free Practice, KeyQuest now shows a regular up/down choice menu instead of relying on `OK` wording.
- Lesson prompts now try to speak real practice words naturally, while letter patterns such as `asas` or `aass` are spelled out more clearly.
- Recent consistency work also tightened the shared menu, dialog, shop, pet, and setup screen patterns so more screens now behave alike.
- Update failures now write `keyquest_error.log`, offer the setup download, and stay local instead of auto-opening a GitHub bug report.
- The Practice Log now uses friendlier dates and durations, includes activity names and results, and can be copied to the clipboard.

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
- Treat the repo as Python 3.9 everywhere unless an explicit migration changes that policy. Source runs, GitHub workflows, and linting are aligned to 3.9 for consistency and TTS compatibility.

## Community

- Use [GitHub Issues](https://github.com/csm120/KeyQuest/issues) for bugs and actionable feature requests.
- Use GitHub Discussions for questions, accessibility feedback, gameplay ideas, and general project conversation.

## Contact

- Website: webfriendlyhelp.com
- Feedback: help@webfriendlyhelp.com
