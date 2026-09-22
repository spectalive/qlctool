"""The layer that makes a wheel-coloured fixture follow a travelling hue.

A look whose colour moves - either rainbow EFX, a two-colour matrix, a cycle of
coloured matrices - says nothing to the four 7R, whose colour is a wheel and
whose red, green and blue do not exist. Before this they sat on whatever detent
the state underneath had last written while the rest of the room swept through
the spectrum: "el arcoiris no funciona con los beam, no hace el color arcoiris"
(owner, 2026-09-22), which `rule_colour_animation_wheel` now refuses.

The fixture's own answer is in its definition: the BEAM 230W 7R's colour
channel carries two continuous rainbow ranges above its fourteen detents
(`RotationClockwiseFastToSlow` at 128-191). So this generates one Scene that
puts every wheel-coloured fixture's colour wheel into that range, to run
*beside* a travelling-hue look as its own layer - nothing else, no dimmer and
no shutter, so whoever owns the intensity keeps owning it.
"""

from collections.abc import Sequence

from .. import roles
from ..capability import FixtureCapabilities
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..workspace import Workspace

ROTATION = "Rotation"


def generate_beam_rainbow_spin(
    workspace: Workspace,
    capabilities: Sequence[FixtureCapabilities],
    name: str = "Color Beam - Arcoiris (capa)",
    path: str = "Color Beam",
) -> int | None:
    """One Scene spinning every wheel-only colour wheel; None when there is none."""
    values: dict[int, list[tuple[int, int]]] = {}
    for caps in capabilities:
        if caps.has_role(roles.RED) or not caps.has_role(roles.COLOR_MACRO):
            continue
        pairs: list[tuple[int, int]] = []
        for offset, positions in caps.capabilities_for_role(roles.COLOR_MACRO):
            spin = next((p for p in positions if p.preset.startswith(ROTATION)), None)
            if spin is not None:
                pairs.append((offset, spin.middle))
        if pairs:
            values[caps.fixture.fixture_id] = pairs
    if not values:
        return None
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, name, values, path=path))
    return function_id
