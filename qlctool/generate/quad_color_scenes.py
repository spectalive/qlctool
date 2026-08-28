"""The hand-built "4 Colores" looks: four colours dealt across the rig.

DeluxeEventos2 kept four deterministic scenes (85-88) rotating blue, red,
green and white over the heads and the beams - the same deal shifted one seat
each scene, so pressing through them walks every fixture through all four
colours. The generated show replaced them with the two wild multicolor steps
and lost the deterministic rotation (old-vs-new audit, 2026-08-28). This
rebuilds the four looks over the whole colour-capable rig: RGB fixtures take
their dealt colour, the beams take the nearest wheel position for theirs, and
the deal follows patch order the way `Rig Multicolor` does.

Colour only, no intensity: like every wheel step since 2026-08-27, the energy
levels own the dimmers.
"""

from collections.abc import Sequence

from .. import roles
from ..capabilities_of import capabilities_of
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..palette import PALETTE
from ..workspace import Workspace
from .color_scene import color_scene_values
from .wheel_color_values import wheel_color_values

# The old scenes' own deal, in their own order.
QUAD_COLORS: tuple[str, ...] = ("Azul", "Rojo", "Verde", "Blanco")


def generate_quad_color_scenes(
    workspace: Workspace,
    library: FixtureLibrary,
    exclude_fixture_ids: Sequence[int] = (),
    program_gated_ids: Sequence[int] = (),
    path: str = "Colores Rig",
) -> list[int]:
    """One scene per rotation of the four-colour deal; [] when nothing colours."""
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
    for offset in range(len(QUAD_COLORS)):
        values: dict[int, list[tuple[int, int]]] = {}
        for index, capability in enumerate(rgb_caps):
            fixture_id = capability.fixture.fixture_id
            name = QUAD_COLORS[(index + offset) % len(QUAD_COLORS)]
            values.update(color_scene_values(
                caps, PALETTE[name], fixture_ids=[fixture_id],
                dimmer_full=False,
                internal_program_off=fixture_id not in gated,
            ))
        for index, capability in enumerate(wheel_caps, start=len(rgb_caps)):
            name = QUAD_COLORS[(index + offset) % len(QUAD_COLORS)]
            values.update(wheel_color_values(
                caps, name,
                fixture_ids=[capability.fixture.fixture_id], dimmer=None,
            ))
        if not values:
            continue
        function_id = next_function_id(workspace.root)
        workspace.add_function(build_scene(
            function_id, f"Rig 4 Colores {offset + 1}", values, path=path
        ))
        scene_ids.append(function_id)
    return scene_ids
