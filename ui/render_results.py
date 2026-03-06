from ui.a11y import draw_active_panel, draw_controls_hint
from ui.text_wrap import wrap_text


def draw_results_screen(
    *,
    screen,
    text_font,
    small_font,
    screen_w: int,
    screen_h: int,
    fg,
    accent,
    results_text: str,
    focus_assist: bool = False,
):
    lines = wrap_text(text_font, results_text, screen_w - 120, fg)

    y = 150
    block_top = y
    max_width = 0
    total_height = 0
    for ln in lines:
        surf, _ = text_font.render(ln, fg)
        max_width = max(max_width, surf.get_width())
        total_height += surf.get_height() + 16
    import pygame
    panel_rect = pygame.Rect(
        screen_w // 2 - (max_width // 2) - 30,
        block_top - 24,
        max_width + 60,
        max(70, total_height + 20),
    )
    draw_active_panel(screen, panel_rect, accent, fg, strong=focus_assist)
    for ln in lines:
        surf, _ = text_font.render(ln, fg)
        screen.blit(surf, (screen_w // 2 - surf.get_width() // 2, y))
        y += surf.get_height() + 16

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Space/Enter continue; Esc menu",
        screen_w=screen_w,
        y=screen_h - 50,
        accent=accent,
    )
