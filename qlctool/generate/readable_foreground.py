"""Pick a readable console caption colour for a given background."""

RGB = tuple[int, int, int]


def readable_foreground(rgb: RGB) -> RGB:
    """Black on a light colour, white on a dark one - so the caption survives."""
    r, g, b = rgb
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return (0, 0, 0) if luminance > 150 else (255, 255, 255)
