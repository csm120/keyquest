try:
    import ctypes as _ctypes

    _HCF_HIGHCONTRASTON = 0x00000001
    _SPI_GETHIGHCONTRAST = 0x0042

    class _HIGHCONTRAST(_ctypes.Structure):
        _fields_ = [
            ("cbSize", _ctypes.c_uint),
            ("dwFlags", _ctypes.c_uint),
            ("lpszDefaultScheme", _ctypes.c_wchar_p),
        ]

    def _is_windows_high_contrast() -> bool:
        try:
            hc = _HIGHCONTRAST()
            hc.cbSize = _ctypes.sizeof(hc)
            ok = _ctypes.windll.user32.SystemParametersInfoW(
                _SPI_GETHIGHCONTRAST, hc.cbSize, _ctypes.byref(hc), 0
            )
            return bool(ok and (hc.dwFlags & _HCF_HIGHCONTRASTON))
        except Exception:
            return False

except Exception:
    def _is_windows_high_contrast() -> bool:
        return False


def detect_theme(darkdetect_module=None) -> str:
    """Detect system theme, default to dark mode (white on black).

    Checks Windows High Contrast mode first, then uses darkdetect for
    light/dark detection. Falls back to dark if detection fails.
    """
    if _is_windows_high_contrast():
        return "high_contrast"

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
        (90, 130, 190),  # WCAG AA compliant: 5.77:1 contrast ratio (nudged for margin)
    )
