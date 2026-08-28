"""Park the moving heads somewhere sensible, so stillness is a look.

Constant movement reads as noise: the professional habit is to treat motion as a
level, not as a background, which means the quiet part of the night needs the
heads *held* rather than merely not driven. A head with nothing driving its pan
and tilt sits wherever the last effect abandoned it - often at one end of its
travel, pointing at the ceiling - so "no movement" has to be a scene of its own.

Mid-scale on both axes is the middle of the fixture's own travel, which for a
head hanging from a truss is straight out over the room and for one standing on
a flightcase is straight up. The fine channels go to zero so a 16-bit head lands
on the coarse value rather than a quarter-step past it.
"""

from .. import roles
from ..capabilities_of import capabilities_of
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..workspace import Workspace

MID = 127
# The hand-built `Cabezas Reposo` did not park the 7R beams mid-travel: it laid
# them at pan 0, tilt 130, aimed by eye on the real rig (old-vs-new audit,
# 2026-08-28 - a beam at pan 127 is not the same look as pan 0). The washes
# stay at mid-scale; a beam is a fixture with a gobo wheel, the same line the
# movement families draw.
BEAM_PAN = 0
BEAM_TILT = 130


def generate_home_position(
    workspace: Workspace,
    library: FixtureLibrary,
    name: str = "Cabezas Centro",
    path: str = "Movimiento",
) -> int | None:
    """One scene holding every mover parked. None if none move."""
    values: dict[int, list[tuple[int, int]]] = {}
    for caps in capabilities_of(workspace.root, library):
        if not (caps.has_role(roles.PAN) and caps.has_role(roles.TILT)):
            continue
        beam = caps.has_role(roles.GOBO)
        pairs: list[tuple[int, int]] = []
        for role, value in (
            (roles.PAN, BEAM_PAN if beam else MID),
            (roles.TILT, BEAM_TILT if beam else MID),
            (roles.PAN_FINE, 0),
            (roles.TILT_FINE, 0),
        ):
            pairs += [(offset, value) for offset in caps.offsets_for_role(role)]
        values[caps.fixture.fixture_id] = sorted(pairs)

    if not values:
        return None

    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, name, values, path=path))
    return function_id
