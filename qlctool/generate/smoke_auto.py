"""A smoke machine that runs itself: a burst, then a long wait, forever.

Nobody is at the console during these shows, so the haze has to come on its own.
Two scenes and a looping chaser do it, and the pump is only ever driven from
here - every other generator skips smoke fixtures, because a machine caught in
an "all dimmers up" scene runs until the tank is empty.
"""

from dataclasses import dataclass

from .. import roles
from ..capabilities_of import capabilities_of
from ..fog_offsets import fog_offsets
from ..functions.chaser import build_chaser
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..workspace import Workspace


@dataclass(frozen=True)
class GeneratedSmoke:
    on_id: int
    off_id: int
    chaser_id: int


def generate_smoke_auto(
    workspace: Workspace,
    library: FixtureLibrary,
    burst_ms: int = 2000,
    pause_ms: int = 60000,
    level: int = 255,
    path: str = "Humo",
) -> GeneratedSmoke:
    """Burst/pause the ambient smoke machines; raises when the rig has none.

    Only the fog-only machines: a smoke machine that also carries lights is a
    show machine - a vertical column somebody fires on purpose - and a timer
    that fires four of those every minute all night is a wrong show and four
    empty tanks. Those fire from `vertical_smoke_burst` instead.
    """
    smoke = [
        c for c in capabilities_of(workspace.root, library)
        if c.is_smoke and not c.has_role(roles.RED)
    ]
    if not smoke:
        raise ValueError("no smoke machine in this workspace")

    def scene(name: str, value: int) -> int:
        values = {
            caps.fixture.fixture_id: [
                (offset, value) for offset in fog_offsets(caps)
            ]
            for caps in smoke
        }
        function_id = next_function_id(workspace.root)
        workspace.add_function(build_scene(function_id, name, values, path=path))
        return function_id

    on_id = scene("Humo ON", level)
    off_id = scene("Humo OFF", 0)

    chaser_id = next_function_id(workspace.root)
    # A burst, then the long wait before the next one - so the two steps have
    # their own holds, which is what puts this chaser in PerStep duration mode.
    chaser = build_chaser(
        chaser_id,
        "Humo Auto",
        [on_id, off_id],
        hold=[burst_ms, pause_ms],
        path=path,
    )
    workspace.add_function(chaser)

    return GeneratedSmoke(on_id=on_id, off_id=off_id, chaser_id=chaser_id)
