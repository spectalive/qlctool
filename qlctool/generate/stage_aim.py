"""The heads aimed at the stage: the hand-built show's `Escenario`, kept.

Somebody climbs on stage and the room needs light *there* - the hand-built
console had one button for it, aimed by eye on the real rig and used at every
gig. Those pan/tilt numbers cannot be derived from anything in this repo: they
encode where the stage is from each truss position, so they are carried here
as measured data, keyed by the fixture's DMX address - the one identity that
survives repatching, because it names the cable, not the file.

The measured aims go to the rigged heads patched at those addresses; a spare
the stage plot hides in a flight case is skipped, and an address in the table
with no fixture on it (a repatch that moved things) is skipped rather than
guessed at. Every other rigged mover holds the centre of its family's window
until somebody measures it on site: the two CromoWash the hand-built scene
aimed are spares now, and the MAC WASH that replaced them sat at 127/127, the
wall behind the stage, while `Escenario` was pressed (en-sala DMX audit,
2026-09-26; ruling D7). The scene writes position only - what colour the stage
gets stays with whatever state is running, exactly like the original.
"""

from .. import roles
from ..capabilities_of import capabilities_of
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..names.default_names import default_names
from ..names.names import Names
from ..rigged_fixture_ids import rigged_fixture_ids
from ..workspace import Workspace
from .movement_aim import BEAM_PAN_AIM, BEAM_TILT_AIM, WASH_PAN_AIM, WASH_TILT_AIM

# DMX address (0-based, as patched) -> (pan, tilt), read verbatim out of
# DeluxeEventos2's `Escenario` scene (ID 376) on 2026-08-27.
MEASURED_AIMS: dict[int, tuple[int, int]] = {
    0: (161, 49),  # CromoWash100 #1
    12: (176, 43),  # CromoWash100 #2
    218: (156, 196),  # BEAM 230W 7R #1
    234: (159, 204),  # BEAM 230W 7R #2
    250: (159, 192),  # BEAM 230W 7R #3
    266: (162, 189),  # BEAM 230W 7R #4
}


def generate_stage_aim(
    workspace: Workspace,
    library: FixtureLibrary,
    path: str | None = None,
    names: Names | None = None,
) -> int | None:
    """The stage-aim scene named by `names`, or None when no measured mover is rigged."""
    vocabulary = default_names() if names is None else names
    path = vocabulary.display("path_movement") if path is None else path
    values: dict[int, list[tuple[int, int]]] = {}
    hung = rigged_fixture_ids(workspace.root)
    rigged = [
        caps
        for caps in capabilities_of(workspace.root, library)
        if caps.fixture.fixture_id in hung
        and caps.has_role(roles.PAN)
        and caps.has_role(roles.TILT)
    ]
    # The look is the measured one: with no measured mover rigged there is no
    # stage to aim at, only a guess.
    if not any(caps.fixture.address in MEASURED_AIMS for caps in rigged):
        return None
    for caps in rigged:
        centre = (
            (BEAM_PAN_AIM, BEAM_TILT_AIM)
            if caps.has_role(roles.GOBO)
            else (WASH_PAN_AIM, WASH_TILT_AIM)
        )
        pan, tilt = MEASURED_AIMS.get(caps.fixture.address, centre)
        pairs: list[tuple[int, int]] = []
        for role, value in (
            (roles.PAN, pan),
            (roles.TILT, tilt),
            (roles.PAN_FINE, 0),
            (roles.TILT_FINE, 0),
        ):
            pairs += [(offset, value) for offset in caps.offsets_for_role(role)]
        if pairs:
            values[caps.fixture.fixture_id] = sorted(pairs)

    if not values:
        return None

    function_id = next_function_id(workspace.root)
    workspace.add_function(
        build_scene(function_id, vocabulary.display("stage_aim"), values, path=path)
    )
    return function_id
