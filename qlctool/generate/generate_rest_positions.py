"""Build the beams' fan and cross, and the washes' hold beside them.

`Beams Abanico` and `Beams Cruce` are the beams' two static rests - the fan
opened once and held, the cross aimed over the neighbour's head - and, as rest
steps of the beams' rotation, the washes keep moving through them on their own
chaser. Pressed as picks, though, they stop the frame's movement, so each gets
a companion: the washes held at their measured window's centre
(`generate_wash_hold`, ruling D7).
"""

from collections.abc import Sequence

from ..fixture_library import FixtureLibrary
from ..names.names import Names
from ..workspace import Workspace
from .generate_cross_position import generate_cross_position
from .generate_fan_position import generate_fan_position
from .generate_wash_hold import generate_wash_hold
from .rest_positions import RestPositions


def generate_rest_positions(
    workspace: Workspace,
    library: FixtureLibrary,
    beams: Sequence[int],
    washes: Sequence[int],
    vocabulary: Names,
) -> RestPositions:
    fan_id = generate_fan_position(workspace, library, beams, names=vocabulary)
    cross_id = generate_cross_position(workspace, library, beams, names=vocabulary)
    rests = [function_id for function_id in (fan_id, cross_id) if function_id is not None]
    hold_id = generate_wash_hold(workspace, library, washes, names=vocabulary) if rests else None
    companions = {rest: [hold_id] for rest in rests} if hold_id is not None else {}
    return RestPositions(fan_id=fan_id, cross_id=cross_id, hold_id=hold_id, companions=companions)
