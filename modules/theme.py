def detect_theme(darkdetect_module=None) -> str:
    """Detect system theme, default to dark mode (white on black)."""
    if darkdetect_module is None:
        try:
            import darkdetect as _darkdetect

            darkdetect_module = _darkdetect
        except Exception:
            darkdetect_module = None

    if darkdetect_module:
        try:
            detected = darkdetect_module.theme()
            if detected == "Light":
                return "light"
            if detected == "Dark":
                return "dark"
        except Exception:
            pass
    return "dark"


def get_theme_colors(theme: str, darkdetect_module=None):
    """Return (BG, FG, ACCENT, HILITE) for a given theme selection."""
    if theme == "auto":
        theme = detect_theme(darkdetect_module)

    if theme == "light":
        return (
            (255, 255, 255),
            (0, 0, 0),
            (0, 100, 200),
            (0, 0, 255),  # Pure blue for better contrast on white background
        )

    if theme == "high_contrast":
        return (
            (0, 0, 0),
            (255, 255, 255),
            (255, 255, 0),  # Yellow for high contrast
            (255, 255, 255),
        )

    return (
        (0, 0, 0),
        (255, 255, 255),  # Pure white on black for maximum contrast
        (180, 220, 255),
        (80, 120, 180),  # WCAG AA compliant: 4.69:1 contrast ratio
    )
