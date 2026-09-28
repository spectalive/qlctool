"""One console button per shape, whichever families draw it, plus the two twins.

Diamond and Leaf merge the beam versions into the same button the wash
versions already have; Ola Suave and Cascada Beams get a button of their own -
their algorithm (Line, Circle) already names an existing button, and merging
into it would fire a wash's plain Line whenever the cascade is pressed, or vice
versa. The twins the hand-built console had and this one only ran inside the
automatic rotation get one button per shape and per way of phasing it, each
spanning both families like the plain shapes do (`twin_movement`, "faltan
movimientos, unos iban a la vez otros iban alternados", owner, 2026-09-22).
"""

from ..functions.build_collection import build_collection
from ..names.names import Names
from ..next_function_id import next_function_id
from ..workspace import Workspace
from .beam_envelopes import (
    BEAM,
    BEAM_ALTERNATE,
    BEAM_ROTATED_SHAPES,
    BEAM_TWIN_SHAPES,
    BEAM_WIDE_SHAPES,
)
from .generated_movements import GeneratedMovements
from .label_of import label_of
from .wash_envelopes import WASH, WASH_ALTERNATE


def movement_shape_buttons(
    workspace: Workspace,
    wash: GeneratedMovements | None,
    beam: GeneratedMovements | None,
    beam_shapes: GeneratedMovements | None,
    beam_wide: GeneratedMovements | None,
    wash_sim: GeneratedMovements | None,
    beam_sim: GeneratedMovements | None,
    wash_alt: GeneratedMovements | None,
    beam_alt: GeneratedMovements | None,
    ola_suave: GeneratedMovements | None,
    cascada_beams: GeneratedMovements | None,
    vocabulary: Names,
    movement_path: str,
) -> tuple[list[int], list[int]]:
    display = vocabulary.display

    def label(shape: str) -> str:
        return label_of(display, shape)

    efx_ids: list[int] = []
    play_pick_ids: list[int] = []
    by_shape: dict[str, list[int]] = {}
    for generated, envelope in (
        (wash, WASH),
        (beam, BEAM),
        (beam_shapes, BEAM_ROTATED_SHAPES),
        (beam_wide, BEAM_WIDE_SHAPES),
    ):
        if generated is None:
            continue
        for shape, efx in zip(envelope.algorithms, generated.efx_ids, strict=True):
            by_shape.setdefault(shape, []).append(efx)
    for shape in WASH.algorithms:
        members = by_shape.get(shape)
        if not members:
            continue
        collection_id = next_function_id(workspace.root)
        workspace.add_function(
            build_collection(
                collection_id,
                vocabulary.render("movement_shape", shape=label(shape)),
                members,
                path=movement_path,
            )
        )
        efx_ids.append(collection_id)
        play_pick_ids.append(collection_id)
    for mode, parts in (
        ("mode_together", ((wash_sim, WASH), (beam_sim, BEAM_TWIN_SHAPES))),
        ("mode_alternating", ((wash_alt, WASH_ALTERNATE), (beam_alt, BEAM_ALTERNATE))),
    ):
        twins: dict[str, list[int]] = {}
        for generated, envelope in parts:
            if generated is None:
                continue
            for shape, efx in zip(envelope.algorithms, generated.efx_ids, strict=True):
                twins.setdefault(shape, []).append(efx)
        for shape in WASH.algorithms:
            members = twins.get(shape)
            if not members:
                continue
            collection_id = next_function_id(workspace.root)
            workspace.add_function(
                build_collection(
                    collection_id,
                    vocabulary.render("movement_shape", shape=f"{label(shape)} {display(mode)}"),
                    members,
                    path=movement_path,
                )
            )
            efx_ids.append(collection_id)
            play_pick_ids.append(collection_id)
    if ola_suave is not None:
        efx_ids.append(ola_suave.efx_ids[0])
    if cascada_beams is not None:
        efx_ids.append(cascada_beams.efx_ids[0])
    return efx_ids, play_pick_ids
