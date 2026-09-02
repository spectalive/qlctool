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
from ..internal_program import internal_program_off_pairs
from ..mode_park import mode_park_pairs
from ..shutter_open import shutter_open_pairs
from ..strobe_off import strobe_off_pairs
from ..white_level import white_level
from ..zoom_wide import zoom_wide_pairs

RGB = tuple[int, int, int]


def color_scene_values(
    capabilities: list[FixtureCapabilities],
    rgb: RGB,
    dimmer_full: bool = True,
    fixture_ids: Sequence[int] | None = None,
    internal_program_off: bool = True,
) -> dict[int, list[tuple[int, int]]]:
    red, green, blue = rgb
    result: dict[int, list[tuple[int, int]]] = {}
    wanted = None if fixture_ids is None else set(fixture_ids)

    for caps in capabilities:
        if wanted is not None and caps.fixture.fixture_id not in wanted:
            continue
        # A fog-only machine has no colour to state. One that carries lights
        # joins like a floor PAR - its pump is a different role, never touched
        # here ("una fuente de luz desde el suelo", owner, 2026-08-29).
        if caps.is_smoke and not caps.is_lit_smoke:
            continue
        if not (
            caps.has_role(roles.RED) or caps.has_role(roles.GREEN) or caps.has_role(roles.BLUE)
        ):
            continue

        pairs: list[tuple[int, int]] = []
        for offset in caps.offsets_for_role(roles.RED):
            pairs.append((offset, red))
        for offset in caps.offsets_for_role(roles.GREEN):
            pairs.append((offset, green))
        for offset in caps.offsets_for_role(roles.BLUE):
            pairs.append((offset, blue))
        # The dedicated white emitter, where there is one: the share of white
        # in the colour, so a white look uses the white LED and a red one says
        # zero to it instead of leaving it to the last look (2026-09-02).
        for offset in caps.offsets_for_role(roles.WHITE):
            pairs.append((offset, white_level(rgb)))
        # The beam's width belongs to the colour, not to the intensity: a
        # caller that leaves the dimmer to the energy levels still owns the
        # shape of the light it is painting, and nothing else writes zoom.
        pairs += zoom_wide_pairs(caps)
        if dimmer_full:
            for offset in caps.offsets_for_role(roles.DIMMER):
                pairs.append((offset, 255))
            pairs += shutter_open_pairs(caps)
            # A strobe-only channel is LTP and a released Flash restores
            # nothing: the scene that owns the light writes the strobe off.
            pairs += strobe_off_pairs(caps)
        # A fixture running its own programme ignores red, green and blue, and
        # nothing resets that channel on its own: state the colour and the
        # fixture is still animating, through a speech included.
        # internal_program_off=False leaves the mode channel to a concurrent
        # owner instead - the wheel writes the panels' RGB all night while
        # `Ciclo Paneles Mixto` decides whether they are listening. Only for a
        # caller that really runs such an owner; `rule_internal_program` holds
        # everyone else to writing the mode off right here.
        if internal_program_off:
            pairs += internal_program_off_pairs(caps)
        # And the fixtures whose self-running channel has no names to match on
        # - the MAC WASH's `Function Mode`, the MiN Wash's macros, the fog
        # machines' colour cycle. Same trap, parked the same way.
        pairs += mode_park_pairs(caps)

        result[caps.fixture.fixture_id] = pairs

    return result
