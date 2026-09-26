"""The colour a pad LED glows while its function is idle."""

from .argb import RGB

# The bridge's measured idle brightness: a sixth of the colour, whole numbers
# (`DIM = 6` in the SMC-PAD LED bridge before its palette moved here).
IDLE_DIVISOR = 6


def pad_idle_colour(active: RGB) -> RGB:
    """`active` dimmed to the idle glow, each channel divided and rounded down."""
    red, green, blue = active
    return (red // IDLE_DIVISOR, green // IDLE_DIVISOR, blue // IDLE_DIVISOR)
