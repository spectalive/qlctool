"""A fixture no colour look reaches: no red, green or blue, and no colour wheel.

The colour looks are where every self-running channel is parked
(`mode_park_pairs`): `color_scene_values` and the pixel base take the fixtures
with RGB, `wheel_color_values` the ones with a colour wheel. A head with
neither - an LED gobo spot, a BEAM 230W 7R without its wheel - is touched by
none of them, so its `Effect` channel was written by nothing and `check` said
`modo sin dueño` (gobo-spot regression rig, 2026-09-25). The looks that light
such a head park it instead, and only such a head: every other fixture is
already parked by the colour it is painted with.
"""

from . import roles
from .capability import FixtureCapabilities


def outside_color_looks(capabilities: FixtureCapabilities) -> bool:
    """True when the fixture has no RGB channel and no colour wheel."""
    if any(capabilities.has_role(role) for role in (roles.RED, roles.GREEN, roles.BLUE)):
        return False
    return capabilities.wheel_for_role(roles.COLOR_MACRO) is None
