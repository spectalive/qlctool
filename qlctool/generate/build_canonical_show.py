"""Build the whole show: content, structure, and a console that runs itself.

The shows this rig plays are unattended - the laptop is left alone and has to
keep changing colour, movement and gobos on its own - so the target is not a
console full of buttons for an operator, it is one AUTO function that brings up
everything at once, with the manual buttons there for when somebody does sit
down. The shape is taken from the hand-built show: colour banks per group with
Random wheels, mixed two-colour looks, gobo and prism animations, movement, and
smoke on a timer.

Each stage is its own module and runs in the order the functions have always
been created, which is what keeps the generated ids - and the Vibra
workspaces - byte for byte the same (2026-09-26, round G: this was one
function of a thousand lines).
"""

from collections.abc import Sequence

from ..description.show_description import ShowDescription
from ..library import FixtureLibrary
from ..workspace import Workspace
from .add_base_looks import add_base_looks
from .add_colour_wheels import add_colour_wheels
from .add_energy_levels import add_energy_levels
from .add_haze_dimmers_strobes import add_haze_dimmers_strobes
from .add_intensity_bases import add_intensity_bases
from .add_moments import add_moments
from .add_movement import add_movement
from .add_panel_looks import add_panel_looks
from .add_pixel_layers import add_pixel_layers
from .add_play_wrappers import add_play_wrappers
from .add_rainbows import add_rainbows
from .add_show_console import add_show_console
from .add_wheel_looks import add_wheel_looks
from .apply_show_tempo import apply_show_tempo
from .canonical_show import CanonicalShow
from .default_matrix_algorithms import MATRIX_ALGORITHMS
from .start_show_build import start_show_build


def build_canonical_show(
    workspace: Workspace,
    library: FixtureLibrary,
    algorithms: Sequence[str | None] = MATRIX_ALGORITHMS,
    matrix_colors: Sequence[str] | None = None,
    with_layout: bool = True,
    plot_path: str | None = None,
    beats: bool = False,
    bpm_tap: bool = False,
    description: ShowDescription | None = None,
) -> CanonicalShow:
    """Strip the workspace to its patch and generate a self-running show on it."""
    build = start_show_build(
        workspace, library, algorithms, matrix_colors, plot_path, beats, bpm_tap, description
    )
    add_base_looks(build)
    add_panel_looks(build)
    add_pixel_layers(build)
    add_movement(build)
    add_wheel_looks(build)
    add_haze_dimmers_strobes(build)
    add_colour_wheels(build)
    add_rainbows(build)
    add_intensity_bases(build)
    add_energy_levels(build)
    add_moments(build)
    add_play_wrappers(build)
    apply_show_tempo(build)
    button_ids = add_show_console(build) if with_layout else []

    functions = [f for f in workspace.engine if f.tag.endswith("}Function")]
    return CanonicalShow(
        banks=build.banks,
        matrix_ids=build.matrix_ids,
        efx_ids=build.movement.efx_ids,
        gobo_ids=build.gobos.scene_ids + build.beam_colors.scene_ids,
        prism_ids=build.prisms.scene_ids + build.beam_subsets.prism_scene_ids,
        play_wrappers=build.play_wrappers,
        colour_flash_ids=build.colour_flash_ids,
        master_ids=build.master,
        button_ids=button_ids,
        function_count=len(functions),
        stage_placed=build.stage_placed,
    )
