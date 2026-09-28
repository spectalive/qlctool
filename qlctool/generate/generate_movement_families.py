"""Movement per optics family: washes and beams stop sharing one geometry.

All twelve movers ran the same 100x100 EFX at the same speed, which tuned the
show for neither of them - a wash's soft wide beam wants big slow curves, a 7R
needle at that size and speed drags a hard line through faces (Codex review,
2026-08-27). The family split is read off capability: a mover with a gobo
wheel is a beam, one without is a wash - the same line `rule_movement_families`
draws.

Each family gets its own envelope per tempo of the night:

- **Suave** (Ambiente): two wide slow shapes per family. The beams used to hold
  the static fan through this whole level instead - four minutes of a needle
  nailed to one spot, which the room reads as broken rather than as rest ("las
  7R no se mueven", owner, 2026-08-29, watching AUTO). The fan is still their
  rest, but as one step of the Normal rotation, where it lasts a step and not a
  level.
- **Normal** (Fiesta): both families move, each at its own size and speed, and
  the fan sits in the beams' rotation as a rest step - stillness between
  moving blocks instead of motion as wallpaper.
- **Rapido** (Peak): both families, twice the pace, sized to their optics.

Every envelope is centred on its family's own measured audience window
(`audience_window`) rather than on mid-travel, which is where QLC+ puts a
figure nobody aims - the floor for the beams, the back wall for the washes -
and sized so the whole figure fits inside that window.

`Movimientos Cabezas` and `Movimientos Rapidos` remain the console's names for
"everything moves": Collections over the family chasers, so the buttons, the
moments and the muscle memory survive the split.
"""

from collections.abc import Collection

from ..fixture_library import FixtureLibrary
from ..functions.build_collection import build_collection
from ..names.default_names import default_names
from ..names.names import Names
from ..next_function_id import next_function_id
from ..workspace import Workspace
from .assemble_beam_rotation import assemble_beam_rotation
from .assemble_slow_rotation import assemble_slow_rotation
from .assemble_wash_rotation import assemble_wash_rotation
from .generate_family_variants import generate_family_variants
from .generate_rest_positions import generate_rest_positions
from .generated_families import GeneratedFamilies
from .movement_figure_buttons import movement_figure_buttons
from .movement_shape_buttons import movement_shape_buttons
from .resolve_movement_rig import resolve_movement_rig


def generate_movement_families(
    workspace: Workspace,
    library: FixtureLibrary,
    mirrored_ids: Collection[int] = (),
    names: Names | None = None,
) -> GeneratedFamilies:
    """Per-family movement, the fan, and the two rig-wide Collections, named by `names`."""
    vocabulary = default_names() if names is None else names
    display = vocabulary.display

    rig = resolve_movement_rig(workspace, library, vocabulary)
    if rig is None:
        return GeneratedFamilies()

    variants = generate_family_variants(
        workspace,
        library,
        rig.washes,
        rig.beams,
        rig.rigged,
        rig.rigged_washes,
        rig.rigged_beams,
        mirrored_ids,
        vocabulary,
        rig.movement_path,
        rig.soft_path,
        rig.fast_path,
    )

    rests = generate_rest_positions(workspace, library, rig.beams, rig.washes, vocabulary)

    slow_id = assemble_slow_rotation(
        workspace, variants.slow, variants.ola_suave, variants.slow_beam, vocabulary, rig.soft_path
    )
    wash_id = assemble_wash_rotation(
        workspace,
        variants.wash,
        variants.wash_sim,
        variants.ola_wash,
        variants.unison_wash,
        vocabulary,
        rig.movement_path,
    )
    beam_id = assemble_beam_rotation(
        workspace,
        variants.beam,
        variants.beam_sim,
        variants.beam_shapes,
        variants.cascada_beams,
        variants.ola_beam,
        variants.unison_beam,
        rests.fan_id,
        rests.cross_id,
        vocabulary,
        rig.movement_path,
    )

    efx_ids, play_pick_ids = movement_shape_buttons(
        workspace,
        variants.wash,
        variants.beam,
        variants.beam_shapes,
        variants.beam_wide,
        variants.wash_sim,
        variants.beam_sim,
        variants.wash_alt,
        variants.beam_alt,
        variants.ola_suave,
        variants.cascada_beams,
        vocabulary,
        rig.movement_path,
    )
    movement_figure_buttons(
        workspace,
        variants.ola_wash,
        variants.ola_beam,
        variants.unison_wash,
        variants.unison_beam,
        rests.fan_id,
        rests.cross_id,
        vocabulary,
        rig.movement_path,
        efx_ids,
        play_pick_ids,
    )

    def _both(name: str, first: int | None, second: int | None, path: str) -> int | None:
        members = [m for m in (first, second) if m is not None]
        if not members:
            return None
        collection_id = next_function_id(workspace.root)
        workspace.add_function(build_collection(collection_id, name, members, path=path))
        return collection_id

    fast_wash_id = variants.fast_wash.chaser_id if variants.fast_wash is not None else None
    fast_beam_id = variants.fast_beam.chaser_id if variants.fast_beam is not None else None
    return GeneratedFamilies(
        slow_id=slow_id,
        slow_beam_id=variants.slow_beam.chaser_id if variants.slow_beam is not None else None,
        wash_id=wash_id,
        beam_id=beam_id,
        fast_wash_id=fast_wash_id,
        fast_beam_id=fast_beam_id,
        fan_id=rests.fan_id,
        cabezas_id=_both(display("head_movements"), wash_id, beam_id, rig.movement_path),
        rapidos_id=_both(
            display("fast_movements"),
            fast_wash_id,
            fast_beam_id,
            rig.fast_path,
        ),
        efx_ids=efx_ids,
        play_pick_ids=play_pick_ids,
        dial_ids=[m for m in (wash_id, beam_id) if m is not None],
        pick_companions=rests.companions,
    )
