"""The same alternation over the wheel-coloured fixtures of a group.

They alternate among themselves rather than sharing the RGB fixtures'
counter: four beams split two colours two and two, which is what the look
means, instead of all landing on whichever colour their patch index gives.
"""

from collections.abc import Sequence

from .. import roles
from ..fixture_capabilities import FixtureCapabilities
from ..names.names import Names
from .wheel_color_values import wheel_color_values


def wheel_halves(
    capabilities: list[FixtureCapabilities],
    fixture_ids: Sequence[int] | None,
    color_names: tuple[str, str],
    dimmer: int | None,
    names: Names | None = None,
) -> dict[int, list[tuple[int, int]]]:
    ordered = [
        caps
        for caps in capabilities
        if not any(caps.has_role(role) for role in (roles.RED, roles.GREEN, roles.BLUE))
    ]
    if fixture_ids is not None:
        by_id = {caps.fixture.fixture_id: caps for caps in ordered}
        ordered = [by_id[i] for i in fixture_ids if i in by_id]

    values: dict[int, list[tuple[int, int]]] = {}
    for index, caps in enumerate(ordered):
        values.update(
            wheel_color_values(
                [caps],
                color_names[index % 2],
                fixture_ids=[caps.fixture.fixture_id],
                dimmer=dimmer,
                names=names,
            )
        )
    return values
