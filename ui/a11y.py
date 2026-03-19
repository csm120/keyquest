import pygame
from ui.text_wrap import wrap_text


def get_visible_window(item_count: int, current_index: int, max_visible: int):
    """Return the visible slice for a scrollable list centered on the current item."""
    if item_count <= max_visible:
        return 0, item_count

    half = max_visible // 2
    start = max(0, current_index - half)
    end = start + max_visible

    if end > item_count:
        end = item_count
        start = max(0, end - max_visible)

    return start, end


def draw_keystroke_flash(screen, color, alpha: int, screen_w: int, screen_h: int):
    """Draw a brief semi-transparent color overlay for visual keystroke feedback.

    Call each frame while the flash is active; alpha fades out over time.
    """
    flash_surf = pygame.Surface((screen_w, screen_h))
    flash_surf.fill(color)
    flash_surf.set_alpha(alpha)
    screen.blit(flash_surf, (0, 0))


def draw_focus_frame(screen, target_rect, hilite, accent):
    """Draw a high-visibility focus frame that does not rely on color only."""
    outer = target_rect.inflate(28, 14)
    inner = target_rect.inflate(14, 8)
    pygame.draw.rect(screen, accent, outer, width=1, border_radius=8)
    pygame.draw.rect(screen, hilite, inner, width=3, border_radius=8)


def draw_active_panel(screen, target_rect, accent, fg, strong: bool = False):
    """Draw a soft panel behind the active area so it stands out without changing focus logic."""
    panel_rect = target_rect.inflate(80, 46) if strong else target_rect.inflate(60, 36)
    panel = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    if sum(fg) > 380:
        panel.fill((255, 255, 255, 40 if strong else 28))
    else:
        panel.fill((0, 0, 0, 56 if strong else 36))
    screen.blit(panel, panel_rect.topleft)
    pygame.draw.rect(screen, accent, panel_rect, width=2 if strong else 1, border_radius=12)


def draw_secondary_panel(screen, target_rect, accent, fg, strong: bool = False):
    """Draw a quieter panel for secondary but still important content."""
    panel_rect = target_rect.inflate(56, 32) if strong else target_rect.inflate(44, 26)
    panel = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    if sum(fg) > 380:
        panel.fill((255, 255, 255, 24 if strong else 16))
    else:
        panel.fill((0, 0, 0, 34 if strong else 22))
    screen.blit(panel, panel_rect.topleft)
    pygame.draw.rect(screen, accent, panel_rect, width=2 if strong else 1, border_radius=10)


def draw_action_emphasis(screen, target_rect, hilite, strong: bool = False):
    """Draw a stronger visual marker under the active action text."""
    underline_width = min(max(90 if strong else 80, target_rect.width + 24), target_rect.width + (56 if strong else 40))
    underline_x = target_rect.centerx - underline_width // 2
    underline_y = target_rect.bottom + 8
    thickness = 6 if strong else 4
    radius = 5 if strong else 4
    pygame.draw.line(screen, hilite, (underline_x, underline_y), (underline_x + underline_width, underline_y), thickness)
    pygame.draw.circle(screen, hilite, (underline_x - 10, underline_y), radius)
    pygame.draw.circle(screen, hilite, (underline_x + underline_width + 10, underline_y), radius)


def draw_controls_hint(*, screen, small_font, text, screen_w: int, y: int, accent):
    """Draw a consistent controls row across screens."""
    message = f"Controls: {text}"
    lines = wrap_text(small_font, message, max(240, screen_w - 40), accent) or [message]
    sample_surf, _ = small_font.render(lines[0], accent)
    line_height = sample_surf.get_height() + 4
    start_y = y - ((len(lines) - 1) * line_height)
    for idx, line in enumerate(lines):
        surf, _ = small_font.render(line, accent)
        x = screen_w // 2 - surf.get_width() // 2
        screen.blit(surf, (x, start_y + (idx * line_height)))
