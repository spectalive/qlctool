"""The first colour of a deal that a given wheel actually carries.

Dealing a palette across the rig is easy while every fixture is RGB: whatever
seat a fixture draws, three channels can say it. A wheel cannot. It has fifteen
detents, the palette has eighteen names, and `color_wheel_pairs` answers None
for the ones it does not hold - so a beam that draws "Verde Menta" is written
nothing at all and keeps the colour it had, which is the failure
`rule_wheel_colour` was written for.

Walking the deal forward from the seat the fixture drew keeps both properties
that matter: neighbours still differ, because the walk starts at a different
seat for each of them, and every wheel ends up on a real detent.
"""

from collections.abc import Sequence

from ..capability import FixtureCapabilities
from ..color_wheel_match import color_wheel_pairs
from ..names.names import Names


def dealt_wheel_color(
    capability: FixtureCapabilities,
    colors: Sequence[str],
    start: int,
    names: Names | None = None,
) -> str | None:
    """The palette name this wheel carries, from `start` forward; None if none.

    `names` is the show's vocabulary the colour names are spelled in.
    """
    if not colors:
        return None
    for step in range(len(colors)):
        name = colors[(start + step) % len(colors)]
        if color_wheel_pairs(capability, name, names):
            return name
    return None
