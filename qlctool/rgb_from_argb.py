"""Convert a 32-bit ARGB int QLC+ stores back to plain 8-bit RGB."""

from .argb_from_rgb import RGB


def rgb_from_argb(value: int) -> RGB:
    """Inverse of argb_from_rgb; the alpha byte is discarded."""
    return ((value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF)
