# KeyQuest

[![Latest Release](https://img.shields.io/github/v/release/csm120/KeyQuest)](https://github.com/csm120/KeyQuest/releases/latest)

KeyQuest is an accessible typing practice program for keyboard, screen reader, and low-vision users, designed from the ground up for people who rely on screen readers (NVDA, JAWS) or have low vision.

**Quick start** (requires Python 3.9+):

```
pip install -r requirements.txt
py -3.9 keyquest.pyw
```

Downloadable installers and portable ZIPs are on the [Releases page](https://github.com/csm120/KeyQuest/releases).

## For Users

Open [README.html](README.html) in a web browser for the plain-language guide.

Recent user-facing changes are tracked in [WHATS_NEW.md](docs/user/WHATS_NEW.md).

Current keyboard navigation highlights:

- `Home` jumps to the first item and `End` jumps to the last item in menus, lesson lists, options, and post-session choice menus.
- After lessons and Free Practice, KeyQuest now shows a regular up/down choice menu instead of relying on `OK` wording.
- Lesson prompts now try to speak real practice words naturally, while letter patterns such as `asas` or `aass` are spelled out more clearly.

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
