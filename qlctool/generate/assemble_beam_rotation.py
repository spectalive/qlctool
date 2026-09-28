"""Build the beams' rotation, carrying the fan and the cross as rest steps of it.

The beams' rotation carries the fan as a step of its own: a rest the chaser
lands on, not a separate button somebody has to remember. The cross is the
other rest - an X where the fan is a crown - and the wave and the push rotate
among the moving blocks (a scene or EFX as a chaser step is an alternative,
never a concurrent writer, which is what keeps `colores pisados` off the
pan/tilt channels).
"""

from ..functions.build_chaser import build_chaser
from ..names.names import Names
from ..next_function_id import next_function_id
from ..workspace import Workspace
from .beam_envelopes import BEAM
from .generated_movements import GeneratedMovements
from .movement_crossfade_ms import MOVEMENT_CROSSFADE_MS


def assemble_beam_rotation(
    workspace: Workspace,
    beam: GeneratedMovements | None,
    beam_sim: GeneratedMovements | None,
    beam_shapes: GeneratedMovements | None,
    cascada_beams: GeneratedMovements | None,
    ola_beam: GeneratedMovements | None,
    unison_beam: GeneratedMovements | None,
    fan_id: int | None,
    cross_id: int | None,
    vocabulary: Names,
    movement_path: str,
) -> int | None:
    display = vocabulary.display
    beam_id: int | None = None
    if beam is not None:
        steps = (
            list(beam.efx_ids)
            + (list(beam_sim.efx_ids) if beam_sim is not None else [])
            + (list(beam_shapes.efx_ids) if beam_shapes is not None else [])
            + (list(cascada_beams.efx_ids) if cascada_beams is not None else [])
            + (list(ola_beam.efx_ids) if ola_beam is not None else [])
            + (list(unison_beam.efx_ids) if unison_beam is not None else [])
            + ([fan_id] if fan_id is not None else [])
            + ([cross_id] if cross_id is not None else [])
        )
        beam_id = next_function_id(workspace.root)
        workspace.add_function(
            build_chaser(
                beam_id,
                display("beam_movements"),
                steps,
                hold=BEAM.hold,
                fade_in=MOVEMENT_CROSSFADE_MS,
                fade_out=MOVEMENT_CROSSFADE_MS,
                run_order="Random",
                path=movement_path,
            )
        )
    return beam_id
