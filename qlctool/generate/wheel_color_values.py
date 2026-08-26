"""Put a colour on the fixtures whose colour is a wheel, and open them.

The four BEAM 230W 7R have no RGB: red, green and blue do not exist on them, so
every generator built on `color_scene_values` skips them entirely - it takes one
look for a red channel and moves on. That is why "everything white" left them
dark: not dimmed, not the wrong colour, simply never written to.

What they need is three things at once, which is why this is one function and
not three: the wheel position nearest the colour, the dimmer, and the shutter -
a beam with its dimmer at full and its shutter shut is still a beam that is off.
"""

from collections.abc import Sequence

from .. import roles
from ..capability import FixtureCapabilities
from ..color_wheel_match import color_wheel_pairs
from ..shutter_open import shutter_open_pairs


def wheel_color_values(
    capabilities: list[FixtureCapabilities],
    color_name: str,
    fixture_ids: Sequence[int] | None = None,
    dimmer: int = 255,
) -> dict[int, list[tuple[int, int]]]:
    """fixture_values putting the wheel-coloured fixtures on `color_name`.

    A colour the wheel does not carry leaves that fixture out rather than
    parking it on a position that means something else. Smoke is never touched.
    """
    wanted = None if fixture_ids is None else set(fixture_ids)
    values: dict[int, list[tuple[int, int]]] = {}
    for capability in capabilities:
        if wanted is not None and capability.fixture.fixture_id not in wanted:
            continue
        if capability.is_smoke:
            continue
        pairs = color_wheel_pairs(capability, color_name)
        if not pairs:
            continue
        pairs += [(o, dimmer) for o in capability.offsets_for_role(roles.DIMMER)]
        pairs += shutter_open_pairs(capability)
        values[capability.fixture.fixture_id] = pairs
    return values
