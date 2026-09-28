"""The palette a rotation may step by itself: all of it but white (`wheel_palette`)."""

from ..argb_from_rgb import RGB
from .colour_settings import ColourSettings


def wheel_palette_of(colours: ColourSettings) -> dict[str, RGB]:
    """Every palette colour except the show's white, in palette order."""
    return {name: rgb for name, rgb in colours.palette.items() if name != colours.white}
