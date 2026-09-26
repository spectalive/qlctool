"""The channel families a family frame hands between its hook and its picks.

Each family is the set of roles one SoloFrame of the console plays: the
colour, the heads' position, the gobo and the prism. The panels' internal
programme is a family too ("pixel-mode"), but it is one channel of some
fixtures, not a role (`pixel_mode_offset`).
"""

from .. import roles

FAMILIES = {
    "color": frozenset(
        (
            roles.RED,
            roles.GREEN,
            roles.BLUE,
            roles.WHITE,
            roles.CYAN,
            roles.MAGENTA,
            roles.YELLOW,
            roles.COLOR_MACRO,
        )
    ),
    "position": frozenset((roles.PAN, roles.PAN_FINE, roles.TILT, roles.TILT_FINE)),
    "gobo": frozenset((roles.GOBO, roles.GOBO_SHAKE, roles.FOCUS)),
    "prism": frozenset((roles.PRISM, roles.PRISM_ROTATION)),
}
