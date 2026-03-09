from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERSION_FILE = REPO_ROOT / "modules" / "version.py"
README_HTML_FILE = REPO_ROOT / "README.html"


def read_version() -> str:
    match = re.search(
        r'__version__\s*=\s*"([^"]+)"',
        VERSION_FILE.read_text(encoding="utf-8"),
    )
    if not match:
        raise SystemExit("Could not read __version__ from modules/version.py")
    return match.group(1)


def write_version(version: str) -> None:
    source = VERSION_FILE.read_text(encoding="utf-8")
    updated = re.sub(
        r'__version__\s*=\s*"([^"]+)"',
        f'__version__ = "{version}"',
        source,
        count=1,
    )
    if updated == source:
        raise SystemExit("Could not update modules/version.py")
    with open(VERSION_FILE, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(updated)


def sync_readme_version(version: str) -> None:
    """Keep the plain-language guide version text aligned with the app version."""
    source = README_HTML_FILE.read_text(encoding="utf-8")
    updated = source.replace("{{APP_VERSION}}", version)
    updated = re.sub(
        r"(<p><strong>Version )[^<]+(</strong></p>)",
        rf"\g<1>{version}\g<2>",
        updated,
        count=1,
    )
    updated = re.sub(
        r"(<li><strong>Application</strong>: KeyQuest )[^<]+(</li>)",
        rf"\g<1>{version}\g<2>",
        updated,
        count=1,
    )
    with open(README_HTML_FILE, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(updated)


def bump_version(version: str, bump: str) -> str:
    parts = [int(token) for token in version.split(".")]
    while len(parts) < 3:
        parts.append(0)

    major, minor, patch = parts[:3]

    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    if bump == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise SystemExit(f"Unsupported bump type: {bump}")


def get_changed_files() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    files: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) >= 4:
            files.append(line[3:].strip())
    return files


def suggest_bump(files: list[str]) -> str:
    if not files:
        return "patch"

    minor_prefixes = (
        "modules/",
        "games/",
        "keyquest.pyw",
        ".github/workflows/release.yml",
        "tools/build/",
    )
    patch_prefixes = (
        "docs/",
        "site/",
        "README",
        "Sentences/",
        "tools/dev/write_keyquest_blog_post.py",
        "tools/dev/build_pages_site.py",
    )

    for path in files:
        normalized = path.replace("\\", "/")
        if normalized == "modules/version.py":
            continue
        if normalized.startswith(minor_prefixes):
            return "minor"

    for path in files:
        normalized = path.replace("\\", "/")
        if normalized.startswith(patch_prefixes):
            continue
        return "minor"

    return "patch"


def main() -> None:
    parser = argparse.ArgumentParser(description="Suggest or apply a KeyQuest release version bump.")
    parser.add_argument("--suggest", action="store_true", help="Print the suggested bump type.")
    parser.add_argument("--apply", choices=["patch", "minor", "major"], help="Apply a version bump.")
    args = parser.parse_args()

    files = get_changed_files()

    if args.suggest:
        print(suggest_bump(files))
        return

    if args.apply:
        current = read_version()
        new_version = bump_version(current, args.apply)
        write_version(new_version)
        sync_readme_version(new_version)
        print(new_version)
        return

    parser.error("Use --suggest or --apply.")


if __name__ == "__main__":
    main()
