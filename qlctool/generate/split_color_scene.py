"""Two colours at once, alternating across a group - the show's "Rojo / Azul".

The hand-built show's widest colour range does not come from more colours, it
comes from *mixing*: odd fixtures on one colour, even fixtures on the other, so
the room reads as two colours rather than one wash. This builds those looks, for
every ordered pair of a colour set, which is what the original's 38-step
"Rueda Colores Dobles" steps through.
"""

from collections.abc import Sequence

from .. import roles
from ..capability import FixtureCapabilities
from ..internal_program import internal_program_off_pairs
from ..shutter_open import shutter_open_pairs
from .wheel_color_values import wheel_color_values

RGB = tuple[int, int, int]


def split_color_scene_values(
    capabilities: list[FixtureCapabilities],
    first: RGB,
    second: RGB,
    fixture_ids: Sequence[int] | None = None,
    dimmer_full: bool = True,
    color_names: tuple[str, str] | None = None,
) -> dict[int, list[tuple[int, int]]]:
    """Alternate two colours across the colour-capable fixtures, in patch order.

    fixture_ids restricts and orders the alternation - pass a fixture group's
    members to split that group rather than the whole rig.

    color_names are the palette names of the same two colours. Given them, the
    split also reaches the fixtures whose colour is a wheel and not three
    channels: without it, a group holding a BEAM 230W 7R walks thirty pairs of
    colours with the beams stuck on whatever they had.
    """
    wanted = None if fixture_ids is None else list(fixture_ids)
    ordered = [
        caps for caps in capabilities
        if caps.has_role(roles.RED) or caps.has_role(roles.GREEN)
        or caps.has_role(roles.BLUE)
    ]
    if wanted is not None:
        by_id = {caps.fixture.fixture_id: caps for caps in ordered}
        ordered = [by_id[i] for i in wanted if i in by_id]

    result: dict[int, list[tuple[int, int]]] = {}
    for index, caps in enumerate(ordered):
        red, green, blue = first if index % 2 == 0 else second
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
        pairs += internal_program_off_pairs(caps)
        result[caps.fixture.fixture_id] = pairs

    if color_names is not None:
        result.update(
            _wheel_halves(capabilities, wanted, color_names)
        )
    return result


def _wheel_halves(
    capabilities: list[FixtureCapabilities],
    fixture_ids: Sequence[int] | None,
    color_names: tuple[str, str],
) -> dict[int, list[tuple[int, int]]]:
    """The same alternation over the wheel-coloured fixtures of the group.

    They alternate among themselves rather than sharing the RGB fixtures'
    counter: four beams split two colours two and two, which is what the look
    means, instead of all landing on whichever colour their patch index gives.
    """
    ordered = [
        caps for caps in capabilities
        if not any(
            caps.has_role(role)
            for role in (roles.RED, roles.GREEN, roles.BLUE)
        )
    ]
    if fixture_ids is not None:
        by_id = {caps.fixture.fixture_id: caps for caps in ordered}
        ordered = [by_id[i] for i in fixture_ids if i in by_id]

    values: dict[int, list[tuple[int, int]]] = {}
    for index, caps in enumerate(ordered):
        values.update(
            wheel_color_values(
                [caps], color_names[index % 2], fixture_ids=[caps.fixture.fixture_id]
            )
        )
    return values
