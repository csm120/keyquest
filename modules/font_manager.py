"""Font creation and DPI scaling helpers.

Centralises the logic for choosing font sizes based on the user's
font_scale setting and the system DPI, so keyquest_app.py only needs
to call build_fonts() when the setting changes.
"""

from modules import config as app_config


def detect_dpi_scale() -> float:
    """Return the system DPI scale factor (1.0 = 100%, 1.25 = 125%, etc.)."""
    try:
        import ctypes
        dpi = ctypes.windll.user32.GetDpiForSystem()
        return max(1.0, dpi / 96.0)
    except Exception:
        return 1.0


def build_fonts(font_scale_setting: str):
    """Create and return (title_font, text_font, small_font) at the scaled size.

    Args:
        font_scale_setting: "auto", "100%", "125%", or "150%" from Settings.

    Returns:
        Tuple of three pygame.freetype.Font objects.
    """
    import pygame.freetype

    if font_scale_setting == "auto":
        scale = detect_dpi_scale()
    else:
        try:
            scale = float(font_scale_setting.rstrip("%")) / 100.0
        except Exception:
            scale = 1.0
    scale = max(1.0, min(scale, 2.0))

    title_sz = max(24, round(app_config.TITLE_SIZE * scale))
    text_sz = max(18, round(app_config.TEXT_SIZE * scale))
    small_sz = max(14, round(app_config.SMALL_SIZE * scale))

    title_font = pygame.freetype.SysFont(app_config.FONT_NAME, title_sz)
    text_font = pygame.freetype.SysFont(app_config.FONT_NAME, text_sz)
    small_font = pygame.freetype.SysFont(app_config.FONT_NAME, small_sz)

    return title_font, text_font, small_font
