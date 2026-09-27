"""The movers on one colour, everything else on the other.

Colour only, like the solid steps: intensity belongs to the levels.
"""

from collections.abc import Sequence

from ..fixture_capabilities import FixtureCapabilities
from ..names.names import Names
from .color_scene_values import color_scene_values
from .wheel_color_values import wheel_color_values


def contrast_values(
    caps: list[FixtureCapabilities],
    head_ids: Sequence[int],
    rest_ids: Sequence[int],
    heads_color: str,
    rest_color: str,
    excluded: set[int],
    values_of: dict[str, tuple[int, int, int]],
    vocabulary: Names,
) -> dict[int, list[tuple[int, int]]]:
    lit_heads = [fid for fid in head_ids if fid not in excluded]
    values = color_scene_values(
        caps, values_of[heads_color], fixture_ids=lit_heads, dimmer_full=False
    )
    values.update(
        color_scene_values(caps, values_of[rest_color], fixture_ids=rest_ids, dimmer_full=False)
    )
    for color, fixture_ids in ((heads_color, head_ids), (rest_color, rest_ids)):
        values.update(
            wheel_color_values(caps, color, fixture_ids=fixture_ids, dimmer=None, names=vocabulary)
        )
    return values
