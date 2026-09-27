"""The colour a bank or mix button wears: the palette colour its scene is named after.

Moved verbatim out of `live_console` (2026-09-27 split).
"""

from collections.abc import Mapping

from ..argb import argb_from_rgb
from ..vc.appearance import DEFAULT


def swatch(name: str, palette: Mapping[str, tuple[int, int, int]], second: bool = False) -> str:
    """The ARGB of the palette colour a scene is named after, or Default."""
    parts = [p.strip() for p in name.split(" / ")]
    text = parts[1] if second and len(parts) > 1 else parts[0]
    for color_name in sorted(palette, key=len, reverse=True):
        if text == color_name or text.startswith(f"{color_name} "):
            return str(argb_from_rgb(palette[color_name]))
    return DEFAULT
