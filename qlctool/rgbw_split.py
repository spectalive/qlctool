"""Split an (r, g, b) request into the four emitters a RGBW fixture really has.

The first white-emitter fix (2026-09-02) wrote `min(r, g, b)` to the White
channel and left red, green and blue exactly as asked. That adds the white LED
*on top of* a colour that already carried its own white share, so every tinted
look came out pale: `Luz Charla`, the warm (255, 214, 170), arrived as R255
G214 B170 plus W170 - white with a memory of amber, indistinguishable from
`Blanco Total` ("charla y blanco son lo mismo", owner, 2026-09-22), and the
colour hits read as "mezclados con blanco".

The achromatic share belongs to one emitter, not to two. So it is subtracted
from the three colour LED when it is handed to the white one: the hue and the
saturation of the request survive, and a colour that meant warm stays warm. A
saturated colour is unchanged, its white share being zero.

The exception is the colour that has no hue to lose: red, green and blue all
equal - the full white of the work light and the flashes, and the greys. There
the split would trade brightness for nothing, so every emitter runs, which is
also what keeps a white step of the wheel as bright on the heads as on the
bars, whose only white is RGB.
"""

RGBW = tuple[int, int, int, int]
RGB = tuple[int, int, int]


def rgbw_split(rgb: RGB) -> RGBW:
    """(red, green, blue, white) for an (r, g, b) request."""
    white = min(rgb)
    if len(set(rgb)) == 1:
        return (*rgb, white)
    return (rgb[0] - white, rgb[1] - white, rgb[2] - white, white)
