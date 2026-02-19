NATO_PHONETIC_ALPHABET = {
    "a": "alpha",
    "b": "bravo",
    "c": "charlie",
    "d": "delta",
    "e": "echo",
    "f": "foxtrot",
    "g": "golf",
    "h": "hotel",
    "i": "india",
    "j": "juliet",
    "k": "kilo",
    "l": "lima",
    "m": "mike",
    "n": "november",
    "o": "oscar",
    "p": "papa",
    "q": "quebec",
    "r": "romeo",
    "s": "sierra",
    "t": "tango",
    "u": "uniform",
    "v": "victor",
    "w": "whiskey",
    "x": "xray",
    "y": "yankee",
    "z": "zulu",
    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
}


def format_needed_keys_for_speech(keys) -> str:
    """Format keys as 'A, like alpha' for screen reader clarity."""
    parts = []
    for key in keys:
        k = str(key).lower()
        if k in NATO_PHONETIC_ALPHABET:
            parts.append(f"{k.upper()}, like {NATO_PHONETIC_ALPHABET[k]}")
        else:
            parts.append(str(key))
    return ", ".join(parts)


def format_needed_keys_for_display(keys) -> str:
    """Format keys as 'A (like Alpha)' for on-screen display."""
    parts = []
    for key in keys:
        k = str(key).lower()
        if k in NATO_PHONETIC_ALPHABET:
            parts.append(f"{k.upper()} (like {NATO_PHONETIC_ALPHABET[k].title()})")
        else:
            parts.append(str(key).upper())
    return ", ".join(parts)

