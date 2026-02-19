def draw_results_screen(
    *,
    screen,
    text_font,
    screen_w: int,
    fg,
    results_text: str,
):
    lines = []
    words = results_text.split()
    line = ""
    for word in words:
        test = f"{line} {word}".strip()
        surf, _ = text_font.render(test, fg)
        if surf.get_width() > screen_w - 40:
            lines.append(line)
            line = word
        else:
            line = test
    if line:
        lines.append(line)

    y = 150
    for ln in lines:
        surf, _ = text_font.render(ln, fg)
        screen.blit(surf, (screen_w // 2 - surf.get_width() // 2, y))
        y += 40

