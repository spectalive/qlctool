"""The panels' automatic speed ride, back from the hand-built show.

DeluxeEventos2 had `Strobo LED - Random SPEED` on a console button ("Strobo
LED - Speed Auto"): a sequence gliding the panels' speed channel through
160 → 232 → 200 → 255 with a 45-second fade between values and a minute at
each, so the built-in programmes breathe faster and slower over the night
instead of sitting at one pace. The generated show kept only the manual
`Vel. Paneles` fader (old-vs-new audit, 2026-08-28); this rebuilds the ride
as a chaser of four one-channel scenes over the same speed channels the
fader drives.

HTP puts whichever is higher in charge: the ride idles under a raised fader,
and the fader at zero hands the pace back - the same contract the fader
already documents against the cycle's own 200.
"""

from collections.abc import Sequence

from ..functions.chaser import build_chaser
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..workspace import Workspace

# The old sequence's own values and pacing.
SPEED_STEPS = (160, 232, 200, 255)
STEP_HOLD_MS = 60000
STEP_FADE_MS = 45000


def generate_panel_speed_auto(
    workspace: Workspace,
    speed_channels: Sequence[tuple[int, int]],
    path: str = "Efectos Propios",
) -> int | None:
    """The speed-ride chaser, or None when no fixture has a speed channel."""
    if not speed_channels:
        return None

    scene_ids: list[int] = []
    for value in SPEED_STEPS:
        values: dict[int, list[tuple[int, int]]] = {}
        for fixture_id, offset in speed_channels:
            values.setdefault(fixture_id, []).append((offset, value))
        function_id = next_function_id(workspace.root)
        workspace.add_function(build_scene(function_id, f"Vel. Paneles {value}", values, path=path))
        scene_ids.append(function_id)

    chaser_id = next_function_id(workspace.root)
    workspace.add_function(
        build_chaser(
            chaser_id,
            "Vel. Paneles Auto",
            scene_ids,
            fade_in=STEP_FADE_MS,
            hold=STEP_HOLD_MS,
            path=path,
        )
    )
    return chaser_id
