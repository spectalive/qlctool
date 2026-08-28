"""The whole rig on different colours at once: the wheel's wild steps.

Every other step of the rig wheel puts the room on one colour, and the
contrast pairs stop at two. This is the look past both - "algún modo más loco
multicolor" (owner, 2026-08-28): each fixture takes its own colour from the
palette, spread by patch order so neighbours differ, and the beams - whose
colour is a wheel with no RGB - go onto their rainbow-scroll range, the
continuous colour run their wheel carries and nothing had ever driven.

These are scenes, not a chaser of their own: they enter `Rueda Colores` as
steps, so the crazy look appears on the wheel's clock the way every colour
does - one clock, one owner, "de vez en cuando" by Random rotation.
"""

from collections.abc import Sequence

from .. import roles
from ..argb import RGB
from ..capabilities_of import capabilities_of
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..workspace import Workspace
from .color_scene import color_scene_values

ROTATION_PRESET_PREFIX = "Rotation"
# How far into a scroll range to sit: just off the edge, on the slow side.
SCROLL_MARGIN = 5


def generate_multicolor_scenes(
    workspace: Workspace,
    library: FixtureLibrary,
    colors: Sequence[tuple[str, RGB]],
    exclude_fixture_ids: Sequence[int] = (),
    program_gated_ids: Sequence[int] = (),
    variants: Sequence[int] = (0, 3),
    path: str = "Colores Rig",
) -> list[int]:
    """One scene per variant, each fixture on its own palette colour.

    `variants` are offsets into the colour list, so each scene deals the same
    palette differently. `exclude_fixture_ids` keeps the scenes off the
    matrix-painted fixtures (their multicolour is a matrix the step starts
    beside these); `program_gated_ids` get RGB without the mode channel, the
    same contract the wheel's other steps follow.
    """
    caps = capabilities_of(workspace.root, library)
    excluded = set(exclude_fixture_ids)
    gated = set(program_gated_ids)
    rgb_caps = [
        c for c in caps
        if not c.is_smoke and c.fixture.fixture_id not in excluded
        and any(c.has_role(role) for role in (roles.RED, roles.GREEN, roles.BLUE))
    ]
    wheel_caps = [
        c for c in caps
        if not c.is_smoke and c.fixture.fixture_id not in excluded
        and c.has_role(roles.COLOR_MACRO)
        and not any(c.has_role(role) for role in (roles.RED, roles.GREEN, roles.BLUE))
    ]
    if not rgb_caps and not wheel_caps:
        return []

    scene_ids: list[int] = []
    for number, offset in enumerate(variants, start=1):
        values: dict[int, list[tuple[int, int]]] = {}
        for index, capability in enumerate(rgb_caps):
            fixture_id = capability.fixture.fixture_id
            _, rgb = colors[(index + offset) % len(colors)]
            values.update(color_scene_values(
                caps, rgb, fixture_ids=[fixture_id], dimmer_full=False,
                internal_program_off=fixture_id not in gated,
            ))
        for capability in wheel_caps:
            scroll = _scroll_value(capability)
            if scroll is None:
                continue
            wheel_offset, _ = capability.wheel_for_role(roles.COLOR_MACRO)
            values[capability.fixture.fixture_id] = [(wheel_offset, scroll)]
        if not values:
            continue
        function_id = next_function_id(workspace.root)
        workspace.add_function(build_scene(
            function_id, f"Rig Multicolor {number}", values, path=path
        ))
        scene_ids.append(function_id)
    return scene_ids


def _scroll_value(capability) -> int | None:
    """The slow end of the colour wheel's continuous scroll, if it has one.

    Read off the range's preset: FastToSlow puts slow at the top of the range,
    SlowToFast at the bottom. A wheel with no rotation range returns None and
    the fixture is left to the wheel's ordinary colour steps.
    """
    _, positions = capability.wheel_for_role(roles.COLOR_MACRO)
    for position in positions:
        preset = position.preset or ""
        if not preset.startswith(ROTATION_PRESET_PREFIX):
            continue
        if "FastToSlow" in preset:
            return max(position.minimum, position.maximum - SCROLL_MARGIN)
        return min(position.maximum, position.minimum + SCROLL_MARGIN)
    return None
