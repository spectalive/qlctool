"""The beams crossed over the floor: the other classic static look.

The fan opens the needles outward and reads as architecture; the cross aims
each one over the head of its neighbour, so the room sees an X of light where
the fan showed a crown. Same discipline as `fan_position`: a symmetric,
repeatable shape in raw DMX, to be aimed in the real room, with fine channels
zeroed so a 16-bit head lands on the coarse value.

The pans are the fan's reversed: the leftmost head takes the rightmost pan and
the pairs swap inward, which crosses every beam over the centre line without
inventing new travel limits. Tilt stays at the fan's height - over the crowd,
not into it - because a crossed needle through faces is exactly the mistake
the movement families exist to prevent.
"""

from collections.abc import Sequence

from .. import roles
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..names.default_names import default_names
from ..names.names import Names
from ..workspace import Workspace
from .fan_heads import fan_heads
from .fan_position import MID, SPREAD, TILT


def generate_cross_position(
    workspace: Workspace,
    library: FixtureLibrary,
    fixture_ids: Sequence[int],
    name: str | None = None,
    path: str | None = None,
    names: Names | None = None,
) -> int | None:
    """One scene crossing the rigged `fixture_ids`, in the given order. None when under two.

    Pass them across the stage (`stage_ordered`): the pans fall in that order.
    """
    vocabulary = default_names() if names is None else names
    name = vocabulary.display("beams_cross") if name is None else name
    path = vocabulary.display("path_movement") if path is None else path
    wanted = fan_heads(workspace, library, fixture_ids)
    if len(wanted) < 2:
        return None

    count = len(wanted)
    values: dict[int, list[tuple[int, int]]] = {}
    for index, caps in enumerate(wanted):
        pan = MID + SPREAD - round(2 * SPREAD * index / (count - 1))
        pairs: list[tuple[int, int]] = []
        for role, value in (
            (roles.PAN, pan),
            (roles.TILT, TILT),
            (roles.PAN_FINE, 0),
            (roles.TILT_FINE, 0),
        ):
            pairs += [(offset, value) for offset in caps.offsets_for_role(role)]
        values[caps.fixture.fixture_id] = sorted(pairs)

    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, name, values, path=path))
    return function_id
