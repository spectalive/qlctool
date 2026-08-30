"""Park the channel a fixture uses to run itself, on every look that lights it.

`internal_program` handles the fixtures whose self-running effects are *named*:
a mode channel with a "no function" range and an "auto" one, and a second
channel listing the programmes. Most fixtures are not that tidy. The MAC WASH
1915Z declares one blanket `Function Mode` channel over 000-255 - "the manual
gives no ranges" is written into its own definition - the MiN Wash calls its
own `Movement Macros`, the CLB2.4 `Preprogrammed automatic Shows`, and the
vertical fog machines `Colour Change`. Same shape, no names to match on: one
channel that hands the fixture back to itself.

Nothing in the show wrote any of them, which is not the same as writing zero.
An unwritten channel is a channel whose value is whatever the last controller,
the last night or the fixture's own menu left there - and while it is up, the
fixture ignores the colour, the position and the dimmer the show is sending.
That is the failure the owner watched on 2026-08-29 with the two new washes:
"se quedaban mirando para abajo y hacian cosas raras como una especie de
cambios de colores muy rapidos" - the movement was aimed at the measured
window and the colour was a slow wheel, so what the room saw was not the show.

So every look that states a colour parks these channels at zero, the way it
already parks the shutter and the strobe. Zero is what the definitions call
DMX control; a fixture whose menu is in AUTO or SOUND obeys nothing on the
wire and is a job for the display on its back, not for this file.
"""

from . import roles
from .capability import FixtureCapabilities
from .internal_program import internal_program


def mode_park_pairs(capabilities: FixtureCapabilities) -> list[tuple[int, int]]:
    """(offset, 0) for every self-running channel this fixture has.

    Empty for a fixture with a named internal programme: that one has a real
    off value and a generator of its own (`internal_program_off_pairs`), and
    the panels' mode channel is a layer the show *uses*, not a stray.
    """
    if internal_program(capabilities) is not None:
        return []
    return [(offset, 0) for offset in capabilities.offsets_for_role(roles.EFFECT)]
