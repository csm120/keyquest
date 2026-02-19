"""Helpers for speech-friendly text announcements."""

from __future__ import annotations


SPECIAL_CHAR_NAMES = {
    " ": "space",
    "\t": "tab",
    "\n": "new line",
    ";": "semicolon",
    ",": "comma",
    ".": "period",
    "'": "apostrophe",
    "/": "slash",
    "-": "dash",
    ":": "colon",
    "!": "exclamation mark",
    "?": "question mark",
}


def to_speakable_token(ch: str) -> str:
    """Convert one character to a speech-friendly token."""
    if ch in SPECIAL_CHAR_NAMES:
        return SPECIAL_CHAR_NAMES[ch]
    return ch.lower()


def spell_text(text: str) -> str:
    """Spell text character-by-character with separators for SR clarity."""
    if not text:
        return "nothing"
    return ", ".join(to_speakable_token(ch) for ch in text)


def spell_text_for_typing_instruction(text: str) -> str:
    """Spell text for `Type ...` prompts with optional sequence connectors."""
    if not text:
        return "nothing"

    # Add "then" when sequence order is likely easier to follow:
    # - special keys/spaces, or
    # - repeated characters (e.g., "fef", "aa")
    has_special = any(ch in SPECIAL_CHAR_NAMES for ch in text)
    has_repeated = len(set(text.lower())) < len(text.lower())
    separator = ", then " if (has_special or has_repeated) else ", "
    return separator.join(to_speakable_token(ch) for ch in text)


def build_remaining_text_feedback(remaining: str) -> str:
    """Build consistent mismatch/remaining feedback."""
    if not remaining:
        return "Nothing remaining."
    spelled = spell_text(remaining)
    return f"Missing: {spelled}. Remaining text: {remaining}"
