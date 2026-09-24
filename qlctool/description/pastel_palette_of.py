"""The wheel palette taken towards white, for the pastel mode (`pastel_palette`)."""

from ..argb import RGB
from ..pastel import pastel
from .colour_settings import ColourSettings
from .wheel_palette_of import wheel_palette_of


def pastel_palette_of(colours: ColourSettings) -> dict[str, RGB]:
    """Same names and hues as the wheel palette, each blended towards white."""
    return {name: pastel(rgb) for name, rgb in wheel_palette_of(colours).items()}
