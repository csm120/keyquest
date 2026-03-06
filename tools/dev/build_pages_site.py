"""Build a small static Pages site for KeyQuest docs."""

from __future__ import annotations

import html
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "site"
README_HTML = REPO_ROOT / "README.html"
CHANGELOG_MD = REPO_ROOT / "docs" / "user" / "CHANGELOG.md"


def _inline_markup(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    return escaped


def markdown_to_html(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    parts: list[str] = []
    in_list = False
    in_code = False
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            text = " ".join(item.strip() for item in paragraph if item.strip())
            parts.append(f"<p>{_inline_markup(text)}</p>")
            paragraph = []

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            parts.append("</ul>")
            in_list = False

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_paragraph()
            close_list()
            if in_code:
                parts.append("</code></pre>")
                in_code = False
            else:
                parts.append("<pre><code>")
                in_code = True
            continue

        if in_code:
            parts.append(html.escape(line))
            continue

        if not stripped:
            flush_paragraph()
            close_list()
            continue

        if stripped == "---":
            flush_paragraph()
            close_list()
            parts.append("<hr>")
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading_match:
            flush_paragraph()
            close_list()
            level = len(heading_match.group(1))
            text = _inline_markup(heading_match.group(2))
            parts.append(f"<h{level}>{text}</h{level}>")
            continue

        bullet_match = re.match(r"^\s*-\s+(.*)$", line)
        if bullet_match:
            flush_paragraph()
            if not in_list:
                parts.append("<ul>")
                in_list = True
            parts.append(f"<li>{_inline_markup(bullet_match.group(1))}</li>")
            continue

        numbered_match = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if numbered_match:
            flush_paragraph()
            if not in_list:
                parts.append("<ul>")
                in_list = True
            parts.append(f"<li>{_inline_markup(numbered_match.group(1))}</li>")
            continue

        close_list()
        paragraph.append(line)

    flush_paragraph()
    close_list()
    if in_code:
        parts.append("</code></pre>")

    return "\n".join(parts)


def build_changelog_page() -> str:
    body = markdown_to_html(CHANGELOG_MD.read_text(encoding="utf-8"))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>KeyQuest Changelog</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      font-size: 18px;
      line-height: 1.6;
      color: #111;
      background: #fff;
      margin: 0;
    }}
    main {{
      max-width: 900px;
      margin: 0 auto;
      padding: 24px;
    }}
    a {{
      color: #0b57d0;
    }}
    a:focus-visible {{
      outline: 3px solid #111;
      outline-offset: 2px;
    }}
    code, pre {{
      font-family: Consolas, "Courier New", monospace;
    }}
    pre {{
      background: #f4f4f4;
      padding: 12px;
      overflow-x: auto;
    }}
    hr {{
      border: 0;
      border-top: 1px solid #ccc;
      margin: 24px 0;
    }}
  </style>
</head>
<body>
  <main>
    <p><a href="index.html">Back to User Guide</a></p>
    {body}
  </main>
</body>
</html>
"""


def build_index_page() -> str:
    source = README_HTML.read_text(encoding="utf-8")
    nav_link = '<li><a href="changelog.html">Changelog</a></li>'
    if nav_link not in source:
        source = source.replace(
            '<li><a href="#help">Need Help</a></li>',
            '<li><a href="changelog.html">Changelog</a></li>\n      <li><a href="#help">Need Help</a></li>',
        )
    return source


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / ".nojekyll").write_text("", encoding="utf-8")
    (OUTPUT_DIR / "index.html").write_text(build_index_page(), encoding="utf-8")
    (OUTPUT_DIR / "changelog.html").write_text(build_changelog_page(), encoding="utf-8")


if __name__ == "__main__":
    main()
