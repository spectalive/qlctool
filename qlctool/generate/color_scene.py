"""Generate a solid-colour Scene across every colour-capable fixture.

This is the first mass generator: give it an (r,g,b) and it sets the red/green/
blue channels on every fixture that has them - all eight segments of a bar, both
heads of a wash - and drives the dimmer to full so the colour actually shows.
Fixtures with no RGB (a plain smoke machine, a colour-wheel-only mover) are left
untouched. The result is fixture_values ready for build_scene. fixture_ids restricts it to one group -
a colour bank for the heads alone, say.
"""

from collections.abc import Sequence

from .. import roles
from ..capability import FixtureCapabilities
from ..shutter_open import shutter_open_pairs

RGB = tuple[int, int, int]


def color_scene_values(
    capabilities: list[FixtureCapabilities],
    rgb: RGB,
    dimmer_full: bool = True,
    fixture_ids: Sequence[int] | None = None,
) -> dict[int, list[tuple[int, int]]]:
    red, green, blue = rgb
    result: dict[int, list[tuple[int, int]]] = {}
    wanted = None if fixture_ids is None else set(fixture_ids)

    for caps in capabilities:
        if wanted is not None and caps.fixture.fixture_id not in wanted:
            continue
        if caps.is_smoke:
            continue
        if not (
            caps.has_role(roles.RED)
            or caps.has_role(roles.GREEN)
            or caps.has_role(roles.BLUE)
        ):
            continue

        pairs: list[tuple[int, int]] = []
        for offset in caps.offsets_for_role(roles.RED):
            pairs.append((offset, red))
        for offset in caps.offsets_for_role(roles.GREEN):
            pairs.append((offset, green))
        for offset in caps.offsets_for_role(roles.BLUE):
            pairs.append((offset, blue))
        if dimmer_full:
            for offset in caps.offsets_for_role(roles.DIMMER):
                pairs.append((offset, 255))
            pairs += shutter_open_pairs(caps)

        result[caps.fixture.fixture_id] = pairs

    return result
