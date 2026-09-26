"""A colour bank's values with the wheel heads' blades taken back out.

`wheel_color_values` opens a wheel-only head's blade with its colour, because a
colour look is what owns such a head's light (`wheel_blade_offsets`, ruling D8,
2026-09-27). A bank is not a look: it is a held takeover of the colour the
state is showing, and the state keeps owning every dimmer. A bank that opened
the blade would be one more HTP bid, and a held Flash that raises light on the
beams owes them a strobe it has no business firing.
"""

from ..capability import FixtureCapabilities
from ..wheel_blade_offsets import wheel_blade_offsets


def without_wheel_blades(
    capabilities: list[FixtureCapabilities], values: dict[int, list[tuple[int, int]]]
) -> dict[int, list[tuple[int, int]]]:
    """`values` minus every wheel-only head's blade; a head left empty is dropped."""
    blades = {c.fixture.fixture_id: set(wheel_blade_offsets(c)) for c in capabilities}
    kept: dict[int, list[tuple[int, int]]] = {}
    for fixture_id, pairs in values.items():
        remaining = [(o, v) for o, v in pairs if o not in blades.get(fixture_id, set())]
        if remaining:
            kept[fixture_id] = remaining
    return kept
