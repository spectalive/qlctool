"""The static base a chase-driven level stands on: what the chase cannot own.

`Dimmer Chase` only takes fixtures with a dimmer role - the same walk
`generate_dimmer_chases` makes to build its member list. A fixture with none,
like the Chauvet MiN Wash, has no channel the chase could ever touch: its light
lives behind a shutter range instead (`shutter_open_pairs`). So a level that
hands its dimmer fixtures to the chase and drops its old flat intensity scene
would leave that fixture with no owner at all in that level - not shadowed,
just dark, the moment nothing keeps writing its shutter open.

The strobe-only channels are the same gap on a different channel: the levels
that run `Intensidad Ambiente`/`Total` write them off through those scenes,
but a chase level dropped both - so a flash released during the peak left the
Vortex and the panels strobing until the next level's intensity base cleared
it (the same LTP latch `rule_strobe_restore` was written for, one level down).
This scene is that level's owner for both: shutters open where no dimmer
exists, strobes off everywhere.
"""

from collections.abc import Sequence

from .. import roles
from ..capability import FixtureCapabilities
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..shutter_open import shutter_open_pairs
from ..strobe_off import strobe_off_pairs
from ..workspace import Workspace

PATH = "Niveles"


def generate_dimmerless_intensity(
    workspace: Workspace,
    capabilities: Sequence[FixtureCapabilities],
    exclude_fixture_ids: Sequence[int] = (),
    name: str = "Intensidad Peak",
) -> int | None:
    """The chase level's static base. None when no fixture needs one."""
    excluded = set(exclude_fixture_ids)
    values: dict[int, list[tuple[int, int]]] = {}
    for capability in capabilities:
        if capability.is_smoke or capability.fixture.fixture_id in excluded:
            continue
        pairs: list[tuple[int, int]] = []
        if not capability.offsets_for_role(roles.DIMMER):
            pairs += shutter_open_pairs(capability)
        pairs += strobe_off_pairs(capability)
        if pairs:
            values[capability.fixture.fixture_id] = sorted(set(pairs))
    if not values:
        return None
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, name, values, path=PATH))
    return function_id
