"""One ordered, shared figure for the visible beam and wash families."""

from ..efx_shape_identifiers import EFX_SHAPE_IDENTIFIERS
from ..functions.build_chaser import build_chaser
from ..functions.build_collection import build_collection
from ..names.names import Names
from ..next_function_id import next_function_id
from ..workspace import Workspace
from .beam_envelopes import BEAM_TWIN_SHAPES
from .generated_movements import GeneratedMovements
from .movement_crossfade_ms import MOVEMENT_CROSSFADE_MS
from .wash_envelopes import WASH


def assemble_synced_rotation(
    workspace: Workspace,
    wash: GeneratedMovements | None,
    beam: GeneratedMovements | None,
    cascada_beams: GeneratedMovements | None,
    vocabulary: Names,
    path: str,
) -> int | None:
    """Start corresponding simultaneous shapes together on a common clock."""
    if wash is None or beam is None:
        return None
    if len(wash.efx_ids) != len(WASH.algorithms) or len(beam.efx_ids) != len(
        BEAM_TWIN_SHAPES.algorithms
    ):
        return None
    beam_by_shape = dict(zip(BEAM_TWIN_SHAPES.algorithms, beam.efx_ids, strict=True))
    if any(shape not in beam_by_shape for shape in WASH.algorithms):
        return None
    steps: list[int] = []
    for shape, wash_id in zip(WASH.algorithms, wash.efx_ids, strict=True):
        paired_id = next_function_id(workspace.root)
        workspace.add_function(
            build_collection(
                paired_id,
                f"{vocabulary.display('head_movements')} {vocabulary.display(EFX_SHAPE_IDENTIFIERS[shape])}",
                [wash_id, beam_by_shape[shape]],
                path=path,
            )
        )
        steps.append(paired_id)
    if cascada_beams is not None:
        cascade_id = next_function_id(workspace.root)
        workspace.add_function(
            build_collection(
                cascade_id,
                f"{vocabulary.display('head_movements')} {vocabulary.display('cascade_beams')}",
                [wash.efx_ids[0], cascada_beams.efx_ids[0]],
                path=path,
            )
        )
        steps.append(cascade_id)
    chaser_id = next_function_id(workspace.root)
    workspace.add_function(
        build_chaser(
            chaser_id,
            vocabulary.display("head_movements_cycle"),
            steps,
            hold=WASH.hold,
            fade_in=MOVEMENT_CROSSFADE_MS,
            fade_out=MOVEMENT_CROSSFADE_MS,
            run_order="Loop",
            path=path,
        )
    )
    collection_id = next_function_id(workspace.root)
    workspace.add_function(
        build_collection(
            collection_id, vocabulary.display("head_movements"), [chaser_id], path=path
        )
    )
    return collection_id
