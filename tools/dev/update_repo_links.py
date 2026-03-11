"""Update hardcoded GitHub and Pages owner references across text files.

Usage:
    py tools/dev/update_repo_links.py --new-owner webfriendlyhelp
    py tools/dev/update_repo_links.py --old-owner csm120 --new-owner webfriendlyhelp --apply

Without --apply, the script runs in preview mode and reports planned edits.
"""

from __future__ import annotations

import argparse
from pathlib import Path


TEXT_EXTENSIONS = {
    ".md",
    ".html",
    ".py",
    ".ps1",
    ".txt",
    ".yml",
    ".yaml",
    ".json",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old-owner", default="csm120")
    parser.add_argument("--new-owner", required=True)
    parser.add_argument("--repo-name", default="KeyQuest")
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args()


def build_replacements(old_owner: str, new_owner: str, repo_name: str) -> list[tuple[str, str]]:
    return [
        (
            f"https://github.com/{old_owner}/{repo_name}",
            f"https://github.com/{new_owner}/{repo_name}",
        ),
        (
            f"https://{old_owner}.github.io/{repo_name}/",
            f"https://{new_owner}.github.io/{repo_name}/",
        ),
    ]


def is_text_candidate(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[2]
    replacements = build_replacements(args.old_owner, args.new_owner, args.repo_name)
    changed_paths: list[Path] = []

    for path in root.rglob("*"):
        if not path.is_file() or not is_text_candidate(path):
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        updated = original
        for old, new in replacements:
            updated = updated.replace(old, new)

        if updated == original:
            continue

        changed_paths.append(path)
        if args.apply:
            path.write_text(updated, encoding="utf-8")

    mode = "Applied" if args.apply else "Previewed"
    print(f"{mode} owner-link updates in {len(changed_paths)} file(s).")
    for path in changed_paths:
        print(path.relative_to(root))
    if not args.apply:
        print("Run again with --apply to write changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
