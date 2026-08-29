"""The beams opened into a static fan: the classic look, and their rest.

A 7R beam is a 2-degree needle; run it through the wash's wide curves and it
sweeps a wall of light through faces at wash speed. The professional default
for narrow beams in a small room is the opposite of movement: a symmetric fan,
opened once and held, that reads as architecture. It is also the beams' rest
between moving blocks - stillness a room can see, on fixtures whose stillness
is a look.

Pan values spread evenly around mid-travel, tilt held together slightly above
it. Both are first guesses in raw DMX, to be aimed in the real room like the
home position was - the point here is the *shape*, symmetric and repeatable.
Fine channels go to zero so a 16-bit head lands on the coarse value.
"""

from collections.abc import Sequence

from .. import roles
from ..capabilities_of import capabilities_of
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..workspace import Workspace
from .movement_aim import BEAM_PAN_AIM, BEAM_PAN_SPAN, BEAM_TILT_AIM

# The centre of the audience window in pan, and half its width.
MID = BEAM_PAN_AIM
SPREAD = BEAM_PAN_SPAN
# The fan opens across the audience window the owner measured off the desk,
# and rests at its centre in tilt. It used to be built around mid travel with
# a 90-count spread, which was two guesses at once: mid travel is the floor on
# a 7R, and the spread was wider than the whole window (`movement_aim`).
TILT = BEAM_TILT_AIM


def generate_fan_position(
    workspace: Workspace,
    library: FixtureLibrary,
    fixture_ids: Sequence[int],
    name: str = "Beams Abanico",
    path: str = "Movimiento",
) -> int | None:
    """One scene fanning `fixture_ids` symmetrically. None when under two."""
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
        pan = MID - SPREAD + round(2 * SPREAD * index / (count - 1))
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
