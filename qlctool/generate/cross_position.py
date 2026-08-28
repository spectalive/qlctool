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
from ..capabilities_of import capabilities_of
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..workspace import Workspace
from .fan_position import MID, SPREAD, TILT


def generate_cross_position(
    workspace: Workspace,
    library: FixtureLibrary,
    fixture_ids: Sequence[int],
    name: str = "Beams Cruce",
    path: str = "Movimiento",
) -> int | None:
    """One scene crossing `fixture_ids` over the centre. None when under two."""
    wanted = [
        caps
        for caps in capabilities_of(workspace.root, library)
        if caps.fixture.fixture_id in set(fixture_ids)
        and caps.has_role(roles.PAN) and caps.has_role(roles.TILT)
    ]
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
