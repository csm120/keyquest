FRIENDLY_KEY_NAMES = {
    " ": "Space",
    ";": "Semicolon",
    ",": "Comma",
    ".": "Period",
    "/": "Slash",
    "'": "Apostrophe",
    "[": "Left bracket",
    "]": "Right bracket",
    "-": "Minus",
    "=": "Equals",
    "`": "Backtick",
    "\\": "Backslash",
}

LIMITED_PHONETIC_WORDS = {
    "a": "alpha",
    "b": "bravo",
    "c": "charlie",
    "d": "delta",
    "e": "echo",
    "f": "foxtrot",
    "g": "golf",
    "j": "juliet",
    "k": "kilo",
    "p": "papa",
    "t": "tango",
    "v": "victor",
    "z": "zulu",
}


def _friendly_key_name(key) -> str:
    """Return a plain-language key name without phonetic alphabets."""
    text = str(key)
    if len(text) == 1 and text.isalpha():
        return text.upper()
    if len(text) == 1 and text.isdigit():
        return text
    return FRIENDLY_KEY_NAMES.get(text, text.upper())


def phonetic_hint_for_key(key) -> str:
    """Return a limited phonetic hint for confusable letters only."""
    text = str(key).lower()
    hint = LIMITED_PHONETIC_WORDS.get(text, "")
    if not hint:
        return ""
    return f"{text.upper()}, like {hint}"


def format_needed_keys_for_speech(keys) -> str:
    """Format keys for speech with limited phonetic hints for confusable letters."""
    parts = []
    for key in keys:
        hint = phonetic_hint_for_key(key)
        parts.append(hint if hint else _friendly_key_name(key))
    return ", ".join(parts)


def format_needed_keys_for_display(keys) -> str:
    """Format keys for display with limited phonetic hints for confusable letters."""
    parts = []
    for key in keys:
        text = _friendly_key_name(key)
        hint = LIMITED_PHONETIC_WORDS.get(str(key).lower(), "")
        parts.append(f"{text} (like {hint.title()})" if hint else text)
    return ", ".join(parts)
