"""Which value inside an "open" range a scene should actually send.

Not the middle of it. On 2026-08-29, live at the show, the BEAM 230W 7R sat
black on 248 - dead centre of the range its manual calls "241-255 Open" - and
lit at 255, which is the value the hand-built show had always sent. A published
range is a promise about the endpoint it reaches; the values inside it are not
all honoured by the hardware.

So the value is the endpoint the range actually touches: the top of the channel
when the range runs to 255, the bottom when it starts at 0. A range that
touches neither end - the Pro-Lights CromoWash's "0-9 No function" would touch
0, but a floating one would touch nothing - has no endpoint to reach, and the
middle stays the least-bad guess: as far as possible from the neighbours that
mean something else, strobing above all.
"""

from .definition import Capability

CHANNEL_MIN = 0
CHANNEL_MAX = 255


def shutter_open_value(opening: Capability) -> int:
    """The value inside `opening` that opens the shutter on real hardware."""
    if opening.maximum == CHANNEL_MAX:
        return CHANNEL_MAX
    if opening.minimum == CHANNEL_MIN:
        return CHANNEL_MIN
    return opening.middle
