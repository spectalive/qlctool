"""Movement per optics family, the home position and the stage aim.

Moved verbatim out of `build_canonical_show` (2026-09-26, round G); the
functions are created in the order they always were.
"""

from ..monitor_positions import house_right_fixture_ids
from .home_position import generate_home_position
from .movement_families import generate_movement_families
from .show_build import ShowBuild
from .stage_aim import generate_stage_aim


def add_movement(build: ShowBuild) -> None:
    """Movement per family, the heads' home and the measured stage aim."""
    workspace = build.workspace
    library = build.library
    vocabulary = build.vocabulary
    master = build.master
    # Symmetry comes from reversing one side: with every head going the same way
    # round the room sweeps in parallel, and with house right backwards the
    # pairs open and close together. Movement is generated per optics family -
    # washes wide and slow, beams narrow and shorter - because one geometry
    # over both tuned the show for neither (Codex review, 2026-08-27).
    mirrored = house_right_fixture_ids(workspace.root)
    movement = generate_movement_families(
        workspace, library, mirrored_ids=mirrored, names=vocabulary
    )
    if movement.cabezas_id is not None:
        master[vocabulary.display("head_movements")] = movement.cabezas_id
    if movement.rapidos_id is not None:
        master[vocabulary.display("fast_movements")] = movement.rapidos_id
    home_id = generate_home_position(workspace, library, names=vocabulary)
    if home_id is not None:
        # On the console beside the movement shapes: stillness is a look too.
        master[vocabulary.display("heads_centre")] = home_id
    # The hand-built show's stage look, aimed by eye on the real rig and
    # carried as measured data: heads on the stage, colour left to the state.
    stage_aim_id = generate_stage_aim(workspace, library, names=vocabulary)
    if stage_aim_id is not None:
        master[vocabulary.display("stage_aim")] = stage_aim_id
    build.movement = movement
    build.home_id = home_id
    build.stage_aim_id = stage_aim_id
