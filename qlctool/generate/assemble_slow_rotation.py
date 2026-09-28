"""Build the Suave level's rotation: the washes' cascade beside the plain shapes.

The Suave family gets its own cascade wave beside the two plain shapes, then a
Collection over both washes' and beams' soft chasers - `soft_movements`, the
console's name for this level.
"""

from ..functions.build_chaser import build_chaser
from ..functions.build_collection import build_collection
from ..names.names import Names
from ..next_function_id import next_function_id
from ..workspace import Workspace
from .generated_movements import GeneratedMovements
from .movement_crossfade_ms import MOVEMENT_CROSSFADE_MS
from .wash_envelopes import WASH_SLOW


def assemble_slow_rotation(
    workspace: Workspace,
    slow: GeneratedMovements | None,
    ola_suave: GeneratedMovements | None,
    slow_beam: GeneratedMovements | None,
    vocabulary: Names,
    soft_path: str,
) -> int | None:
    display = vocabulary.display
    slow_wash_id: int | None = None
    if slow is not None:
        steps = list(slow.efx_ids) + (list(ola_suave.efx_ids) if ola_suave is not None else [])
        slow_wash_id = next_function_id(workspace.root)
        workspace.add_function(
            build_chaser(
                slow_wash_id,
                display("soft_washes"),
                steps,
                hold=WASH_SLOW.hold,
                fade_in=MOVEMENT_CROSSFADE_MS,
                fade_out=MOVEMENT_CROSSFADE_MS,
                run_order="Random",
                path=soft_path,
            )
        )

    slow_id: int | None = None
    slow_members = [
        member
        for member in (slow_wash_id, slow_beam.chaser_id if slow_beam else None)
        if member is not None
    ]
    if slow_members:
        slow_id = next_function_id(workspace.root)
        workspace.add_function(
            build_collection(slow_id, display("soft_movements"), slow_members, path=soft_path)
        )
    return slow_id
