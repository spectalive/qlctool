"""A fixture no colour look reaches: no red, green or blue, and no colour it can show.

The colour looks are where every self-running channel is parked
(`mode_park_pairs`): `color_scene_values` and the pixel base take the fixtures
with RGB, `wheel_color_values` the ones whose colour wheel carries a colour
the looks can name. A head with neither - an LED gobo spot, a BEAM 230W 7R
without its wheel - is touched by none of them, so its `Effect` channel was
written by nothing and `check` said `modo sin dueño` (gobo-spot regression rig,
2026-09-25). The looks that light such a head park it instead, and only such
a head: every other fixture is already parked by the colour it is painted with.

A wheel whose positions name no colour the looks request is such a head too:
`color_wheel_pairs` finds none of the show's colours on it, so no wheel look
writes it (2026-09-25 review of the gobo-spot fix). The looks only ask for the
show's palette, so a wheel whose one nameable detent is a colour the palette
lacks ("UV" on a show with no purple) is outside them as well (2026-09-26).
The same predicate decides both.
"""

from collections.abc import Iterable

from . import roles
from .capability import FixtureCapabilities
from .color_wheel_match import color_wheel_pairs
from .names.names import Names


def outside_color_looks(
    capabilities: FixtureCapabilities, colours: Iterable[str], names: Names | None = None
) -> bool:
    """True when the fixture has no RGB channel and its wheel shows none of `colours`.

    `colours` are the colours the looks request - the show's palette - spelled
    as identifiers or in `names`, the show's vocabulary.
    """
    if any(capabilities.has_role(role) for role in (roles.RED, roles.GREEN, roles.BLUE)):
        return False
    return not any(color_wheel_pairs(capabilities, colour, names) for colour in colours)
