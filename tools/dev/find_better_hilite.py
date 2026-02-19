"""Find a better HILITE color for dark theme that meets WCAG AA."""

def relative_luminance(rgb):
    """Calculate relative luminance of an RGB color."""
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
    """Calculate contrast ratio between two RGB colors."""
    l1 = relative_luminance(rgb1)
    l2 = relative_luminance(rgb2)

    lighter = max(l1, l2)
    darker = min(l1, l2)

    return (lighter + 0.05) / (darker + 0.05)

BG_DARK = (0, 0, 0)
CURRENT_HILITE = (60, 100, 160)
CURRENT_RATIO = contrast_ratio(BG_DARK, CURRENT_HILITE)

print(f"Current HILITE: {CURRENT_HILITE}")
print(f"Current ratio: {CURRENT_RATIO:.2f}:1")
print(f"Target: >= 4.5:1 for WCAG AA")
print("\nSearching for better blue colors...")
print()

best_candidates = []

# Try variations around the current color, making it lighter
for r in range(60, 150, 10):
    for g in range(100, 200, 10):
        for b in range(160, 256, 10):
            ratio = contrast_ratio(BG_DARK, (r, g, b))
            if 4.5 <= ratio <= 6.0:  # Want something close to 4.5-6 range
                best_candidates.append(((r, g, b), ratio))

# Sort by how close to 4.7 (a good middle ground)
best_candidates.sort(key=lambda x: abs(x[1] - 4.7))

print("Top 10 candidates (similar hue to current, but WCAG AA compliant):")
print("-" * 60)
for color, ratio in best_candidates[:10]:
    print(f"RGB{color} = {ratio:.2f}:1")

print("\nRecommended: Use one of the first few options above.")
print("They maintain the blue tone while meeting WCAG AA standards.")
