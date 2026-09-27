"""The rigged washes held at their window's centre, beside a beam-only look.

`Beams Abanico` and `Beams Cruce` aim the 7R beams and nothing else. As rest
steps of the beams' rotation that is right - the washes' own chaser moves
them meanwhile - but pressed as picks they stop the frame's movement, and the
two MAC WASH were left at 127/127, the wall behind the stage (en-sala DMX
audit, 2026-09-26). Ruling D7: the washes hold the centre of their measured
window until the look is measured for them. It is a scene of its own that the
picks start beside the beams' one: inside the fan it would write the washes'
pan and tilt while their chaser does, which is a `collision`.
"""

from collections.abc import Collection

from .. import roles
from ..capabilities_of import capabilities_of
from ..fixture_library import FixtureLibrary
from ..functions.scene import build_scene
from ..names.default_names import default_names
from ..names.names import Names
from ..next_function_id import next_function_id
from ..rigged_fixture_ids import rigged_fixture_ids
from ..workspace import Workspace
from .movement_aim import WASH_PAN_AIM, WASH_TILT_AIM


def generate_wash_hold(
    workspace: Workspace,
    library: FixtureLibrary,
    fixture_ids: Collection[int],
    names: Names | None = None,
) -> int | None:
    """One scene holding the rigged `fixture_ids` at the washes' aim. None if none.

    Redundant with `Cabezas Suelo` under AUTO and the four moments (Round 3
    floors write the same aim from the same constant), but it is still the
    only thing holding the MACs there under Blanco Total and Todo Negro,
    which start no floors (M-3, 2026-09-27 final review). Do not remove it.
    """
    vocabulary = default_names() if names is None else names
    rigged = rigged_fixture_ids(workspace.root)
    values: dict[int, list[tuple[int, int]]] = {}
    for caps in capabilities_of(workspace.root, library):
        fixture_id = caps.fixture.fixture_id
        if fixture_id not in fixture_ids or fixture_id not in rigged:
            continue
        pairs: list[tuple[int, int]] = []
        for role, value in (
            (roles.PAN, WASH_PAN_AIM),
            (roles.TILT, WASH_TILT_AIM),
            (roles.PAN_FINE, 0),
            (roles.TILT_FINE, 0),
        ):
            pairs += [(offset, value) for offset in caps.offsets_for_role(role)]
        if pairs:
            values[fixture_id] = sorted(pairs)
    if not values:
        return None
    function_id = next_function_id(workspace.root)
    workspace.add_function(
        build_scene(
            function_id,
            vocabulary.display("washes_hold"),
            values,
            path=vocabulary.display("path_movement"),
        )
    )
    return function_id
