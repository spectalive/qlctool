"""Build the washes' rotation by hand, so the twin, the wave and the push are steps of it.

Assembled the same way the beams' rotation is, so the twin, the tilt wave and
the unison push sit among its steps rather than on buttons only.
"""

from ..functions.build_chaser import build_chaser
from ..names.names import Names
from ..next_function_id import next_function_id
from ..workspace import Workspace
from .generated_movements import GeneratedMovements
from .movement_crossfade_ms import MOVEMENT_CROSSFADE_MS
from .wash_envelopes import WASH


def assemble_wash_rotation(
    workspace: Workspace,
    wash: GeneratedMovements | None,
    wash_sim: GeneratedMovements | None,
    ola_wash: GeneratedMovements | None,
    unison_wash: GeneratedMovements | None,
    vocabulary: Names,
    movement_path: str,
) -> int | None:
    display = vocabulary.display
    wash_id: int | None = None
    if wash is not None:
        steps = (
            list(wash.efx_ids)
            + (list(wash_sim.efx_ids) if wash_sim is not None else [])
            + (list(ola_wash.efx_ids) if ola_wash is not None else [])
            + (list(unison_wash.efx_ids) if unison_wash is not None else [])
        )
        wash_id = next_function_id(workspace.root)
        workspace.add_function(
            build_chaser(
                wash_id,
                display("wash_movements"),
                steps,
                hold=WASH.hold,
                fade_in=MOVEMENT_CROSSFADE_MS,
                fade_out=MOVEMENT_CROSSFADE_MS,
                run_order="Random",
                path=movement_path,
            )
        )
    return wash_id
