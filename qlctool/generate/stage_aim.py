"""The heads aimed at the stage: the hand-built show's `Escenario`, kept.

Somebody climbs on stage and the room needs light *there* - the hand-built
console had one button for it, aimed by eye on the real rig and used at every
gig. Those pan/tilt numbers cannot be derived from anything in this repo: they
encode where the stage is from each truss position, so they are carried here
as measured data, keyed by the fixture's DMX address - the one identity that
survives repatching, because it names the cable, not the file.

Only the fixtures the hand-built scene aimed are aimed: the four BEAM 7R and
the two downstage CromoWash. A patched fixture whose address is not in the
table is simply not part of the look, and an address in the table with no
fixture on it (a repatch that moved things) is skipped rather than guessed at.
The scene writes position only - what colour the stage gets stays with
whatever state is running, exactly like the original.
"""

from .. import roles
from ..capabilities_of import capabilities_of
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..workspace import Workspace

NAME = "Escenario"

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
    path: str = "Movimiento",
) -> int | None:
    """The `Escenario` scene, or None when no aimed fixture is patched."""
    values: dict[int, list[tuple[int, int]]] = {}
    for caps in capabilities_of(workspace.root, library):
        aim = MEASURED_AIMS.get(caps.fixture.address)
        if aim is None:
            continue
        pan, tilt = aim
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
    workspace.add_function(build_scene(function_id, NAME, values, path=path))
    return function_id
