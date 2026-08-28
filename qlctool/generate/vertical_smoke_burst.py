"""The vertical fog machines' burst: the column, and the light inside it.

These machines have DMX priority: with the controller plugged in, their own
timer, remote and colour program are dead, so a show that only drives the pump
gets a column nobody lit - the LED stays dark all night (found against the
scanned manual, 2026-08-29). One scene owns everything the burst is: the fog,
the LED dimmer, the colour, and zeros on the strobe and auto-cycle channels so
nothing latches. White, because a lit column reads as CO2.

Held on a flash button, never latched - the pump fogs while the channel is up,
and the tank pays for every second the button is forgotten.
"""

from .. import roles
from ..capabilities_of import capabilities_of
from ..fog_offsets import fog_offsets
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..workspace import Workspace

NAME = "Humo Vertical YA"
# Full white: the brightest the column gets, and the CO2 look the machines
# were bought for.
RGB = (255, 255, 255)


def generate_vertical_smoke_burst(
    workspace: Workspace, library: FixtureLibrary, path: str = "Humo",
) -> int | None:
    """The held burst scene, or None when the rig has no lit smoke machine."""
    machines = [
        c for c in capabilities_of(workspace.root, library)
        if c.is_smoke and c.has_role(roles.RED)
    ]
    if not machines:
        return None
    values: dict[int, list[tuple[int, int]]] = {}
    for caps in machines:
        pairs = [(offset, 255) for offset in fog_offsets(caps)]
        pairs += [(offset, 255) for offset in caps.offsets_for_role(roles.DIMMER)]
        for role, level in zip(
            (roles.RED, roles.GREEN, roles.BLUE), RGB, strict=True
        ):
            pairs += [(offset, level) for offset in caps.offsets_for_role(role)]
        # Parked, explicitly: the strobe and the auto colour cycle are LTP and
        # keep whatever a stray value left on them.
        for role in (roles.STROBE, roles.EFFECT):
            pairs += [(offset, 0) for offset in caps.offsets_for_role(role)]
        values[caps.fixture.fixture_id] = sorted(pairs)
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, NAME, values, path=path))
    return function_id
