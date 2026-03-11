# Contributing to KeyQuest

Thanks for contributing to KeyQuest.

KeyQuest is a Windows typing game built with Python, with a strong focus on keyboard access, screen reader support, low-vision usability, and clear user-facing documentation.

## Before You Start

- Read [README.md](README.md) for the project overview.
- Read [docs/dev/DEVELOPER_SETUP.md](docs/dev/DEVELOPER_SETUP.md) for local setup details.
- Check existing [Issues](https://github.com/WebFriendlyHelp/KeyQuest/issues) and [Discussions](https://github.com/WebFriendlyHelp/KeyQuest/discussions) before opening something new.
- Use Discussions for questions, ideas, and general feedback.
- Use Issues for confirmed bugs, regressions, and concrete feature work.

## Drive-By Contributions

You do not need to be assigned to contribute.

- If you want to work on an issue, leave a short comment so others can see it is in progress.
- For larger changes, open a draft PR early instead of waiting for assignment.
- Small documentation, typo, or focused test fixes can usually go straight to a PR.
- Maintainers may use labels such as `claimed` or `needs maintainer` to keep work visible, but labels are coordination tools, not permission gates.

### Claiming Work

- The first contributor who comments with a clear plan normally gets priority on that issue.
- If there is no visible progress for about 7 days, maintainers may open the issue back up for others.
- If your plans change, leave a quick comment so someone else can pick it up.

## Development Setup

KeyQuest currently targets Python 3.9.

Basic local setup:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python keyquest.pyw
```

Common validation commands:

```powershell
# Check code quality
ruff check .

# Run tests
pytest -q
```

## Accessibility Expectations

Accessibility is part of the definition of done for this project.

When making UI, input, menu, dialog, documentation, or release changes:

- Keep keyboard-only use fully workable.
- Avoid changes that break screen reader announcements or expected spoken feedback.
- Use plain language in user-facing text.
- Provide descriptive alt text for meaningful images.
- Keep focus indicators, contrast, and interaction flow clear.

If you change behavior that affects accessibility, mention it clearly in your pull request.

## Pull Request Process

1. Fork the repo and create a branch from `main`.
2. If the PR relates to an issue, link it in the PR body and mention whether you commented on the issue first.
3. Keep the change focused. Avoid mixing unrelated fixes in one PR.
4. Update tests, docs, or release notes when they are affected.
5. Run `ruff check .` and `pytest -q` before opening the PR.
6. Fill out the PR template completely.

## Release Notes and User-Facing Changes

If your change affects users directly, update [docs/user/WHATS_NEW.md](docs/user/WHATS_NEW.md) in plain language.

Examples:

- new features
- changed controls
- accessibility improvements
- installer or update behavior changes
- wording changes users will notice

## Good First Contributions

Good first contributions usually include:

- documentation fixes
- plain-language improvements
- accessibility text improvements
- small UI consistency fixes
- test coverage for existing behavior

If you want to contribute but do not know where to start, look for issues labeled `good first issue` or `help wanted`.

## Code Style

- Match the existing project style.
- Prefer small, readable changes over broad refactors.
- Do not raise the project Python version unless that migration is intentional and coordinated.
- Do not remove accessibility behavior without a clear replacement.

## Questions

If you are unsure whether something should be an issue, a discussion, or a pull request, start with a Discussion:

https://github.com/WebFriendlyHelp/KeyQuest/discussions
