"""A static intensity owner for the fixtures a dimmer-mode EFX cannot reach.

`Dimmer Chase` only takes fixtures with a dimmer role - the same walk
`generate_dimmer_chases` makes to build its member list. A fixture with none,
like the Chauvet MiN Wash, has no channel the chase could ever touch: its light
lives behind a shutter range instead (`shutter_open_pairs`). So a level that
hands its dimmer fixtures to the chase and drops its old flat intensity scene
would leave that fixture with no owner at all in that level - not shadowed,
just dark, the moment nothing keeps writing its shutter open.

This scene covers exactly that gap: every non-smoke fixture without a dimmer
role, opened the same way `generate_energy_intensity` already opens it. Found
by the same capability walk the chase itself uses, never by name.
"""

from collections.abc import Sequence

from .. import roles
from ..capability import FixtureCapabilities
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..shutter_open import shutter_open_pairs
from ..workspace import Workspace

PATH = "Niveles"


def generate_dimmerless_intensity(
    workspace: Workspace,
    capabilities: Sequence[FixtureCapabilities],
    exclude_fixture_ids: Sequence[int] = (),
    name: str = "Intensidad Peak",
) -> int | None:
    """A Scene opening every fixture with no dimmer role, or None if none exist."""
    excluded = set(exclude_fixture_ids)
    values: dict[int, list[tuple[int, int]]] = {}
    for capability in capabilities:
        if capability.is_smoke or capability.fixture.fixture_id in excluded:
            continue
        if capability.offsets_for_role(roles.DIMMER):
            continue
        pairs = shutter_open_pairs(capability)
        if pairs:
            values[capability.fixture.fixture_id] = sorted(set(pairs))
    if not values:
        return None
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, name, values, path=PATH))
    return function_id
