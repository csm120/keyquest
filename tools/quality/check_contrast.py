"""Check WCAG color contrast compliance for KeyQuest themes."""

from modules import config as app_config
from modules import theme as theme_manager

def relative_luminance(rgb):
    """Calculate relative luminance of an RGB color.

    Formula from WCAG 2.1: https://www.w3.org/TR/WCAG21/#dfn-relative-luminance
    """
    r, g, b = [x / 255.0 for x in rgb]

    def adjust(c):
        if c <= 0.03928:
            return c / 12.92
        else:
            return ((c + 0.055) / 1.055) ** 2.4

    r = adjust(r)
    g = adjust(g)
    b = adjust(b)

    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast_ratio(rgb1, rgb2):
    """Calculate contrast ratio between two RGB colors.

    Formula from WCAG 2.1: https://www.w3.org/TR/WCAG21/#dfn-contrast-ratio
    """
    l1 = relative_luminance(rgb1)
    l2 = relative_luminance(rgb2)

    lighter = max(l1, l2)
    darker = min(l1, l2)

    return (lighter + 0.05) / (darker + 0.05)

def check_wcag_compliance(ratio, text_size):
    """Check if contrast ratio meets WCAG requirements.

    Args:
        ratio: The contrast ratio
        text_size: Font size in pixels

    Returns:
        dict with AA and AAA compliance status
    """
    # Large text: >= 18.66px bold or >= 24px regular
    # For simplicity, we'll consider 28px+ as large text
    is_large = text_size >= 24

    if is_large:
        aa_required = 3.0
        aaa_required = 4.5
    else:
        aa_required = 4.5
        aaa_required = 7.0

    return {
        'ratio': ratio,
        'AA': ratio >= aa_required,
        'AAA': ratio >= aaa_required,
        'aa_required': aa_required,
        'aaa_required': aaa_required
    }

# KeyQuest themes (source of truth: modules/theme.py)
themes = {}
for theme_name in ("dark", "light", "high_contrast"):
    bg, fg, accent, hilite = theme_manager.get_theme_colors(theme_name)
    themes[theme_name] = {"BG": bg, "FG": fg, "ACCENT": accent, "HILITE": hilite}

# Font sizes in KeyQuest
font_sizes = {
    'TITLE_SIZE': app_config.TITLE_SIZE,
    'TEXT_SIZE': app_config.TEXT_SIZE,
    'SMALL_SIZE': app_config.SMALL_SIZE,
}

print("=" * 80)
print("KeyQuest WCAG Color Contrast Compliance Check")
print("=" * 80)
print("\nWCAG 2.1 AA Requirements:")
print("  - Normal text (< 24px): 4.5:1 minimum")
print("  - Large text (>= 24px): 3:1 minimum")
print("\nWCAG 2.1 AAA Requirements:")
print("  - Normal text (< 24px): 7:1 minimum")
print("  - Large text (>= 24px): 4.5:1 minimum")
print("=" * 80)

for theme_name, colors in themes.items():
    print(f"\n{theme_name.upper()} THEME")
    print("-" * 80)

    bg = colors['BG']

    # Check each text color against background
    for color_name in ['FG', 'ACCENT', 'HILITE']:
        fg = colors[color_name]
        ratio = contrast_ratio(bg, fg)

        print(f"\n{color_name} on BG: {fg} on {bg}")
        print(f"  Contrast Ratio: {ratio:.2f}:1")

        for size_name, size in font_sizes.items():
            compliance = check_wcag_compliance(ratio, size)
            aa_status = "PASS" if compliance['AA'] else "FAIL"
            aaa_status = "PASS" if compliance['AAA'] else "FAIL"
            is_large = "large text" if size >= 24 else "normal text"

            print(f"  {size_name} ({size}px, {is_large}):")
            print(f"    AA (req {compliance['aa_required']:.1f}:1): {aa_status}")
            print(f"    AAA (req {compliance['aaa_required']:.1f}:1): {aaa_status}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("Colors should meet at least WCAG 2.1 AA standards for accessibility.")
print("All text in KeyQuest uses font sizes >= 20px, with main text at 28px+")
print("=" * 80)
