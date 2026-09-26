"""The room's blackout, as a scene of the show."""

from collections.abc import Sequence

from .. import roles
from ..capability import FixtureCapabilities
from ..fog_off import fog_off_pairs
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..internal_program import internal_program_off_pairs
from ..shutter_open import shutter_open_pairs
from ..workspace import Workspace
from .show_path import SHOW_PATH


def blackout_scene(workspace: Workspace, caps: Sequence[FixtureCapabilities], name: str) -> int:
    """Everything dark, with smoke pumps at zero and shutters explicitly owned.

    A lit fog machine's LED is part of the room's light and goes dark with the
    rest; its pump is a different role, so zeroing the dimmer cannot stop the
    fog. The pump is therefore written by name, at zero: a blackout that leaves
    a machine fogging is not a blackout, and a room state that never writes the
    pump is a room state a released smoke flash latches against (`fog_off`).

    A labelled mechanical shutter stays in its open range while RGB and dimmer
    remain zero. The state is still black, but a later family pick can introduce
    colour without inheriting a closed shutter from the blackout.
    """
    values: dict[int, list[tuple[int, int]]] = {}
    for capability in caps:
        if capability.is_smoke:
            off = fog_off_pairs(capability)
            if off:
                values[capability.fixture.fixture_id] = sorted(set(off))
        if capability.is_smoke and not capability.is_lit_smoke:
            continue
        offsets = [
            offset
            for role in (roles.RED, roles.GREEN, roles.BLUE, roles.WHITE, roles.DIMMER)
            for offset in capability.offsets_for_role(role)
        ]
        pairs = [(offset, 0) for offset in sorted(offsets)]
        pairs += shutter_open_pairs(capability)
        # And out of its own programme: a blackout that leaves a panel
        # animating in the dark is a blackout that ends the moment somebody
        # raises a dimmer.
        pairs += internal_program_off_pairs(capability)
        pairs += fog_off_pairs(capability)
        if pairs:
            values[capability.fixture.fixture_id] = sorted(set(pairs))
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, name, values, path=SHOW_PATH))
    return function_id
