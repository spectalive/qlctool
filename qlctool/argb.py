"""Convert between plain 8-bit RGB and the 32-bit ARGB ints QLC+ stores.

RGBMatrix colours (`<MonoColor>`, `<EndColor>`) are written as unsigned decimal
ARGB with the alpha byte always opaque - 4294901760 is 0xFFFF0000, red. Every
generator works in (r, g, b) and converts here, so no caller has to think in
hex.
"""

OPAQUE_ALPHA = 0xFF000000

RGB = tuple[int, int, int]


def argb_from_rgb(rgb: RGB) -> int:
    """Return the opaque 32-bit ARGB int QLC+ writes for this colour."""
    red, green, blue = rgb
    return OPAQUE_ALPHA | (red << 16) | (green << 8) | blue


def rgb_from_argb(value: int) -> RGB:
    """Inverse of argb_from_rgb; the alpha byte is discarded."""
    return ((value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF)
