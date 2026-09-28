"""Sort the rig into washes and beams, stage-ordered, or say there is nothing to move.

The first step of generate_movement_families: read every mover's capabilities,
split it by whether it carries a gobo wheel, and order both families the way
the room sees them - rigged left to right, spares after - so a spare never
takes a phase slot or an every-other place (en-sala DMX audit, 2026-09-26).
"""

from .. import roles
from ..capabilities_of import capabilities_of
from ..fixture_library import FixtureLibrary
from ..names.names import Names
from ..rigged_fixture_ids import rigged_fixture_ids
from ..stage_ordered import stage_ordered
from ..workspace import Workspace
from .movement_rig import MovementRig


def resolve_movement_rig(
    workspace: Workspace, library: FixtureLibrary, vocabulary: Names
) -> MovementRig | None:
    display = vocabulary.display
    movement_path = display("path_movement")
    soft_path = display("path_soft_movement")
    fast_path = display("path_fast_movement")
    washes: list[int] = []
    beams: list[int] = []
    for caps in capabilities_of(workspace.root, library):
        if not (caps.has_role(roles.PAN) and caps.has_role(roles.TILT)):
            continue
        family = beams if caps.has_role(roles.GOBO) else washes
        family.append(caps.fixture.fixture_id)
    if not washes and not beams:
        # A rig with nothing that moves (2026-09-26, round G): no movement at
        # all, which every caller reads as "absent" from the empty families.
        return None
    # Every figure takes the heads as the room sees them - rigged left to
    # right, spares after - so a spare never takes a phase slot or an
    # every-other place (en-sala DMX audit, 2026-09-26).
    rigged = rigged_fixture_ids(workspace.root)
    washes = stage_ordered(workspace.root, washes)
    beams = stage_ordered(workspace.root, beams)
    # A wave's offsets are loop/(heads+1) apart, so a spare in the row takes a
    # slot of it: six hidden washes put the two MACs a ninth of a loop apart
    # instead of a third (Round 2 review of the en-sala audit, 2026-09-27).
    # The waves run over the rigged heads alone, or every head when none is.
    rigged_washes = [i for i in washes if i in rigged] or washes
    rigged_beams = [i for i in beams if i in rigged] or beams
    return MovementRig(
        washes=washes,
        beams=beams,
        rigged=rigged,
        rigged_washes=rigged_washes,
        rigged_beams=rigged_beams,
        movement_path=movement_path,
        soft_path=soft_path,
        fast_path=fast_path,
    )
