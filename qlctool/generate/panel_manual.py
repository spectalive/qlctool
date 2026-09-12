"""The panels listening: manual mode, lit, ready for whatever RGB is running.

Half of `Ciclo Paneles Mixto`. The rig-wide colour wheel writes the panels'
red, green and blue on every step all night, and this scene is what makes them
*show* it: the mode channel back to manual, the intensity open, the strobe
parked off. It states no colour of its own on purpose - the wheel is the one
colour clock in the room, and a second scene naming colours would be a second
one ("van con los colores a su bola" is the bug this design is built around).
"""

from collections.abc import Sequence

from .. import roles
from ..capability import FixtureCapabilities
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..internal_program import internal_program_off_pairs
from ..shutter_open import shutter_open_pairs
from ..strobe_off import strobe_off_pairs
from ..workspace import Workspace


def generate_panel_manual(
    workspace: Workspace,
    capabilities: Sequence[FixtureCapabilities],
    fixture_ids: Sequence[int],
    name: str = "Paneles Manual",
    path: str = "Efectos Propios",
    include_intensity: bool = True,
) -> int | None:
    """Manual mode plus optional intensity support on `fixture_ids`. None when empty."""
    wanted = set(fixture_ids)
    values: dict[int, list[tuple[int, int]]] = {}
    for capability in capabilities:
        if capability.fixture.fixture_id not in wanted or capability.is_smoke:
            continue
        pairs = internal_program_off_pairs(capability)
        if not pairs:
            continue
        if include_intensity:
            pairs += [(offset, 255) for offset in capability.offsets_for_role(roles.DIMMER)]
            pairs += shutter_open_pairs(capability)
            pairs += strobe_off_pairs(capability)
        values[capability.fixture.fixture_id] = sorted(set(pairs))
    if not values:
        return None
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, name, values, path=path))
    return function_id
