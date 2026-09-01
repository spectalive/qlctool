"""The whole rig on different colours at once: the wheel's wild steps.

Every other step of the rig wheel puts the room on one colour, and the
contrast pairs stop at two. This is the look past both - "algún modo más loco
multicolor" (owner, 2026-08-28): each fixture takes its own colour from the
palette, spread by patch order so neighbours differ.

The beams take a detent of their wheel like everybody else. They used to be
sent to the wheel's rainbow-scroll range instead, which reads as the same idea
and is not: a scroll range does not name a colour, it spins the wheel, and a
2-degree beam looking through a wheel that is between two detents shows half of
one colour and half of the next - "se queda como una media luna" (owner,
2026-08-29, live under AUTO). The scroll's slow end made it worse, because the
wheel then sits split for most of a minute.

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
from .dealt_wheel_color import dealt_wheel_color
from .wheel_color_values import wheel_color_values


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
        c
        for c in caps
        if not (c.is_smoke and not c.is_lit_smoke)
        and c.fixture.fixture_id not in excluded
        and any(c.has_role(role) for role in (roles.RED, roles.GREEN, roles.BLUE))
    ]
    wheel_caps = [
        c
        for c in caps
        if not c.is_smoke
        and c.fixture.fixture_id not in excluded
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
            values.update(
                color_scene_values(
                    caps,
                    rgb,
                    fixture_ids=[fixture_id],
                    dimmer_full=False,
                    internal_program_off=fixture_id not in gated,
                )
            )
        names = [name for name, _ in colors]
        for index, capability in enumerate(wheel_caps, start=len(rgb_caps)):
            name = dealt_wheel_color(capability, names, index + offset)
            if name is None:
                continue
            values.update(
                wheel_color_values(
                    caps,
                    name,
                    fixture_ids=[capability.fixture.fixture_id],
                    dimmer=None,
                )
            )
        if not values:
            continue
        function_id = next_function_id(workspace.root)
        workspace.add_function(
            build_scene(function_id, f"Rig Multicolor {number}", values, path=path)
        )
        scene_ids.append(function_id)
    return scene_ids
