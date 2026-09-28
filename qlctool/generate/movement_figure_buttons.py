"""The wave and the push, each a Collection spanning both families, plus the two rests.

The wave and the push span both families, so their buttons are Collections the
way Diamond and Leaf are - one press, both optics. On the beams alone the push
is `Linea Simultaneo` under another name - same line, size, speed and phase -
which is a second button for one look (`twin_movement`, 2026-09-26): only the
washes' slow push makes it a figure of its own. The fan and the cross join the
play page's picks last, beside every button built so far.
"""

from ..functions.build_collection import build_collection
from ..names.names import Names
from ..next_function_id import next_function_id
from ..workspace import Workspace
from .generated_movements import GeneratedMovements


def movement_figure_buttons(
    workspace: Workspace,
    ola_wash: GeneratedMovements | None,
    ola_beam: GeneratedMovements | None,
    unison_wash: GeneratedMovements | None,
    unison_beam: GeneratedMovements | None,
    fan_id: int | None,
    cross_id: int | None,
    vocabulary: Names,
    movement_path: str,
    efx_ids: list[int],
    play_pick_ids: list[int],
) -> None:
    display = vocabulary.display

    def _figure(name: str, *parts: GeneratedMovements | None) -> None:
        members = [generated.efx_ids[0] for generated in parts if generated is not None]
        if not members:
            return
        collection_id = next_function_id(workspace.root)
        workspace.add_function(
            build_collection(
                collection_id,
                name,
                members,
                path=movement_path,
            )
        )
        efx_ids.append(collection_id)
        play_pick_ids.append(collection_id)

    _figure(display("vertical_wave"), ola_wash, ola_beam)
    if unison_wash is not None:
        _figure(display("unison_sweep"), unison_wash, unison_beam)
    play_pick_ids += [function_id for function_id in (fan_id, cross_id) if function_id is not None]
