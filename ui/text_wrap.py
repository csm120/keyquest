def wrap_text(font, text: str, max_width: int, measure_color):
    """Wrap text into lines that fit within max_width pixels using the given font."""
    words = (text or "").split()
    if not words:
        return []

    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        test_surf, _ = font.render(test_line, measure_color)
        if test_surf.get_width() <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)
    return lines

