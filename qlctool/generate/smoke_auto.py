"""A smoke machine that runs itself: a burst, then a long wait, forever.

Nobody is at the console during these shows, so the haze has to come on its own.
Two scenes and a looping chaser do it, and the pump is only ever driven from
here - every other generator skips smoke fixtures, because a machine caught in
an "all dimmers up" scene runs until the tank is empty.
"""

from dataclasses import dataclass

from .. import roles
from ..capabilities_of import capabilities_of
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
    """Burst/pause the smoke machines on a loop; raises when the rig has none."""
    smoke = [c for c in capabilities_of(workspace.root, library) if c.is_smoke]
    if not smoke:
        raise ValueError("no smoke machine in this workspace")

    def scene(name: str, value: int) -> int:
        values = {
            caps.fixture.fixture_id: [
                (offset, value) for offset in caps.offsets_for_role(roles.DIMMER)
            ]
            for caps in smoke
        }
        function_id = next_function_id(workspace.root)
        workspace.add_function(build_scene(function_id, name, values, path=path))
        return function_id

    on_id = scene("Humo ON", level)
    off_id = scene("Humo OFF", 0)

    chaser_id = next_function_id(workspace.root)
    chaser = build_chaser(
        chaser_id, "Humo Auto", [on_id, off_id], hold=burst_ms, path=path
    )
    # The second step is the wait between bursts, so it has its own hold.
    steps = [c for c in chaser if c.tag.endswith("}Step")]
    steps[1].set("Hold", str(pause_ms))
    workspace.add_function(chaser)

    return GeneratedSmoke(on_id=on_id, off_id=off_id, chaser_id=chaser_id)
