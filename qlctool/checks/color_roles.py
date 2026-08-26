"""The roles two functions must never drive at once, and the ones they may.

Dimmer and shutter are shared on purpose: QLC+ mixes them HTP, two functions
asking for full brightness both get what they wanted, and the whole design of
"a colour bed underneath, a level on top" depends on it.

Colour and position are the opposite. HTP on red, green and blue does not
choose between two colours, it adds them - red from a wheel plus blue from a
matrix is magenta, and a third source is white. A wheel channel driven by two
functions lands between two detents. Pan and tilt driven by a static scene and
an EFX at the same time is a head that shakes.
"""

from .. import roles

COLOUR = (
    roles.RED, roles.GREEN, roles.BLUE, roles.WHITE, roles.AMBER, roles.UV,
    roles.CYAN, roles.MAGENTA, roles.YELLOW,
)
WHEELS = (roles.COLOR_MACRO, roles.GOBO, roles.PRISM)
POSITION = (roles.PAN, roles.PAN_FINE, roles.TILT, roles.TILT_FINE)

# Everything a second, concurrent function must not also be driving.
CONTESTED = COLOUR + WHEELS + POSITION
