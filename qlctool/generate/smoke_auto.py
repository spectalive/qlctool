"""A smoke machine that runs itself: a burst, then a long wait, forever.

Nobody is at the console during these shows, so the haze has to come on its own.
Two scenes and a looping chaser do it, and the pump is only ever driven from
here - every other generator skips smoke fixtures, because a machine caught in
an "all dimmers up" scene runs until the tank is empty.

How long that wait is, is not something a file can decide. It depends on the
room, the door, the air conditioning and the night: "estaria bien poder tocar
eso desde la consola en el show" (owner, 2026-08-30). A QLC+ speed dial cannot
do it - a two-step chaser with a 2 s burst and a minutes-long pause is in
PerStep duration mode, and a dial writes the function's own duration, which
PerStep ignores. So the interval is a set of chasers, one per rhythm, in a
solo frame: pressing one stops the others, which is the same "one at a time"
the room states already use, and each of them is still just this generator
with a different pause.
"""

from dataclasses import dataclass, field

from .. import roles
from ..capabilities_of import capabilities_of
from ..fog_offsets import fog_offsets
from ..functions.chaser import build_chaser
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..workspace import Workspace


# The rhythms the console offers, in minutes of pause between bursts. The
# first is the default - the one AUTO starts and the one the key toggles - and
# it is the 60 s this show ran on before there was a choice.
SMOKE_INTERVALS_MIN = (1, 2, 4, 8)


@dataclass(frozen=True)
class GeneratedSmoke:
    on_id: int
    off_id: int
    chaser_id: int
    # name -> function id, default first: the solo frame the console builds.
    interval_ids: dict[str, int] = field(default_factory=dict)


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

    # A burst, then the long wait before the next one - so the two steps have
    # their own holds, which is what puts this chaser in PerStep duration mode.
    def timer(name: str, wait_ms: int) -> int:
        function_id = next_function_id(workspace.root)
        workspace.add_function(build_chaser(
            function_id, name, [on_id, off_id],
            hold=[burst_ms, wait_ms], path=path,
        ))
        return function_id

    chaser_id = timer("Humo Auto", pause_ms)
    interval_ids = {"Humo Auto": chaser_id}
    for minutes in SMOKE_INTERVALS_MIN[1:]:
        name = f"Humo Auto {minutes} min"
        interval_ids[name] = timer(name, minutes * 60_000)

    return GeneratedSmoke(
        on_id=on_id, off_id=off_id, chaser_id=chaser_id,
        interval_ids=interval_ids,
    )
