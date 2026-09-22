"""A palette colour taken towards white, for the room's quiet colour mode.

The owner asked the automatic colour to come in three flavours: "colores
simples, colores completos, colores pastel tenues" (2026-09-22). The first two
are subsets of the palette; the third is not in it, and cannot be - a pastel is
the same hue with less of it.

So a pastel is the colour blended towards white by a fixed share. That keeps the
hue exactly where the palette put it (the ratios between the three primaries are
untouched by adding the same amount to each) and raises the achromatic part,
which `rgbw_split` then hands to the white emitter where a fixture has one - so
a pastel on a MAC WASH is its white LED plus a little colour, which is what a
pastel physically is, rather than three LED at low mixed output.
"""

RGB = tuple[int, int, int]
FULL = 255
# Just over half way to white: enough that the room reads it as tenue rather
# than as the same colour dimmed, and not so much that magenta and rose stop
# being distinguishable.
SHARE = 0.55


def pastel(rgb: RGB, share: float = SHARE) -> RGB:
    """`rgb` blended `share` of the way to white."""
    return tuple(round(value + (FULL - value) * share) for value in rgb)  # type: ignore[return-value]
