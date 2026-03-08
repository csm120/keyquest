from ui.a11y import draw_active_panel, draw_action_emphasis, draw_controls_hint, draw_focus_frame, draw_secondary_panel
from ui.text_wrap import wrap_text


def draw_results_screen(
    *,
    screen,
    title_font,
    text_font,
    small_font,
    screen_w: int,
    screen_h: int,
    fg,
    accent,
    hilite,
    title: str,
    instructions: str,
    results_text: str,
    options: list[str],
    current_index: int,
    focus_assist: bool = False,
):
    title_surf, _ = title_font.render(title, accent)
    title_rect = title_surf.get_rect(topleft=(screen_w // 2 - title_surf.get_width() // 2, 40))
    screen.blit(title_surf, title_rect)

    instruction_lines = wrap_text(small_font, instructions, screen_w - 120, accent)
    y = title_rect.bottom + 20
    for ln in instruction_lines:
        surf, _ = small_font.render(ln, accent)
        screen.blit(surf, (screen_w // 2 - surf.get_width() // 2, y))
        y += surf.get_height() + 10

    y += 12
    lines = wrap_text(text_font, results_text, screen_w - 160, fg)

    block_top = y
    max_width = 0
    total_height = 0
    for ln in lines:
        surf, _ = text_font.render(ln, fg)
        max_width = max(max_width, surf.get_width())
        total_height += surf.get_height() + 14
    import pygame
    panel_rect = pygame.Rect(
        screen_w // 2 - (max_width // 2) - 30,
        block_top - 24,
        max_width + 60,
        max(70, total_height + 24),
    )
    draw_active_panel(screen, panel_rect, accent, fg, strong=focus_assist)
    for ln in lines:
        surf, _ = text_font.render(ln, fg)
        screen.blit(surf, (screen_w // 2 - surf.get_width() // 2, y))
        y += surf.get_height() + 14

    y = panel_rect.bottom + 26
    for idx, option in enumerate(options):
        prefix = "> " if idx == current_index else "  "
        color = hilite if idx == current_index else fg
        surf, _ = text_font.render(f"{prefix}{option}", color)
        rect = surf.get_rect(topleft=(screen_w // 2 - surf.get_width() // 2, y))
        if idx == current_index:
            draw_secondary_panel(screen, rect, accent, fg, strong=focus_assist)
            draw_focus_frame(screen, rect, hilite, accent)
            draw_action_emphasis(screen, rect, hilite, strong=focus_assist)
        screen.blit(surf, rect)
        y += surf.get_height() + 18

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Up/Down choose; Enter or Space select; Esc menu",
        screen_w=screen_w,
        y=screen_h - 50,
        accent=accent,
    )
