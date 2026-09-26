"""The play page's manual picks, wrapped so a pick takes over its family.

Moved verbatim out of `build_canonical_show` (2026-09-26, round G); the
functions are created in the order they always were.
"""

from .play_wrappers import generate_play_wrappers
from .show_build import ShowBuild


def add_play_wrappers(build: ShowBuild) -> None:
    """The wrappers the play page's picks start."""
    workspace = build.workspace
    vocabulary = build.vocabulary
    builtins = build.builtins
    panel_manual_id = build.panel_manual_id
    movement = build.movement
    stage_aim_id = build.stage_aim_id
    shake = build.shake
    dealt = build.dealt
    gobos = build.gobos
    prisms = build.prisms
    spins = build.spins
    beam_subsets = build.beam_subsets
    unison = build.unison
    rainbow_ids = build.rainbow_ids
    # The hand picks are the wheel's plain colours, not every step it takes:
    # the contrast looks and the wild multicolour steps belong to the automatic
    # rotation, and picking one by hand is a look nobody asked for. With
    # eighteen colours in the full mode since 2026-09-22, they are also what
    # keeps the COLOR frame two rows tall (`rule_console` measures it).
    color_step_ids = list(unison.solid_step_ids)
    play_wrappers = generate_play_wrappers(
        workspace,
        color_ids=color_step_ids,
        rainbow_ids=rainbow_ids,
        panel_effect_ids=builtins.scene_ids,
        panel_manual_id=panel_manual_id,
        movement_ids=[
            *movement.play_pick_ids,
            *([stage_aim_id] if stage_aim_id is not None else []),
        ],
        gobo_ids=[*gobos.scene_ids[1:-2], *dealt, *shake.scene_ids],
        prism_ids=[*prisms.scene_ids[1:], *beam_subsets.prism_scene_ids, *spins.scene_ids],
        names=vocabulary,
    )
    build.play_wrappers = play_wrappers
