"""A fixture no colour look reaches: no red, green or blue, and no colour it can show.

The colour looks are where every self-running channel is parked
(`mode_park_pairs`): `color_scene_values` and the pixel base take the fixtures
with RGB, `wheel_color_values` the ones whose colour wheel carries a colour
the looks can name. A head with neither - an LED gobo spot, a BEAM 230W 7R
without its wheel - is touched by none of them, so its `Effect` channel was
written by nothing and `check` said `modo sin dueño` (gobo-spot regression rig,
2026-09-25). The looks that light such a head park it instead, and only such
a head: every other fixture is already parked by the colour it is painted with.

A wheel whose positions name nothing in `WHEEL_NAMES` is such a head too:
`color_wheel_pairs` finds no colour on it, so no wheel look writes it
(2026-09-25 review of the gobo-spot fix). The same predicate decides both.
"""

from . import roles
from .capability import FixtureCapabilities
from .color_wheel_match import WHEEL_NAMES, color_wheel_pairs


def outside_color_looks(capabilities: FixtureCapabilities) -> bool:
    """True when the fixture has no RGB channel and no wheel colour a look can name."""
    if any(capabilities.has_role(role) for role in (roles.RED, roles.GREEN, roles.BLUE)):
        return False
    return not any(color_wheel_pairs(capabilities, colour) for colour in WHEEL_NAMES)
