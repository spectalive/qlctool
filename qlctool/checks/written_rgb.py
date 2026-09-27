"""The (r, g, b) a scene writes on one fixture, exactly as written.

No white folded back in (that is `fixture_colour`): the raw triple is what a
rule needs when it asks whether two fixtures were handed the same channel
values. None when the fixture lacks one of the three or the scene leaves any
unwritten or unpredictable.
"""

from collections.abc import Mapping

from .. import roles
from ..fixture_capabilities import FixtureCapabilities

RGB = (roles.RED, roles.GREEN, roles.BLUE)


def written_rgb(
    capability: FixtureCapabilities, written: Mapping[int, int | None]
) -> tuple[int, int, int] | None:
    stated: list[int] = []
    for role in RGB:
        values = [
            value
            for offset in capability.offsets_for_role(role)
            if (value := written.get(offset)) is not None
        ]
        if not values:
            return None
        stated.append(max(values))
    red, green, blue = stated
    return (red, green, blue)
