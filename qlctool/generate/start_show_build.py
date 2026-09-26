"""Strip a workspace to its patch and open the build every stage of the show adds to.

Moved verbatim out of `build_canonical_show` (2026-09-26, round G): the
description resolved into the show's words, the rig bound to the interface
and the pad it is driven from, the stage placed, the wheels kept from fading.
"""

from ..capabilities_of import capabilities_of
from ..controllers.midi_pad_named import midi_pad_named
from ..description.contrast_pairs_of import contrast_pairs_of
from ..description.description_names import description_names
from ..description.localize_description import localize_description
from ..description.pastel_palette_of import pastel_palette_of
from ..description.show_description import ShowDescription
from ..description.wheel_palette_of import wheel_palette_of
from ..exclude_fade import pin_wheel_fades
from ..library import FixtureLibrary
from ..output_binding import pin_generic_output
from ..skeleton import strip_to_skeleton
from ..stage_plot import load_stage_plot
from ..vibra.vibra_description import vibra_description
from ..workspace import Workspace
from .show_build import ShowBuild
from .stage_layout import generate_stage_layout, unplaced_fixtures
from .stage_plot_layout import apply_stage_plot


def start_show_build(
    workspace: Workspace,
    library: FixtureLibrary,
    plot_path: str | None,
    beats: bool,
    description: ShowDescription | None,
) -> ShowBuild:
    """The workspace stripped and bound, and the build its stages share."""
    source = description if description is not None else vibra_description()
    vocabulary = description_names(source)
    described = localize_description(source, vocabulary)
    colours = described.colours
    wheel = wheel_palette_of(colours)
    pastels = pastel_palette_of(colours)
    contrasts = contrast_pairs_of(colours)
    beats = beats or described.timing.beats
    strip_to_skeleton(workspace, vocabulary)
    # Whatever machine the source file was saved on, the show binds to the
    # USB-DMX interface that is actually plugged in (docs/rig.md; the three
    # shipped files disagreed about serial numbers, old-vs-new audit
    # 2026-08-28).
    pin_generic_output(workspace.root)
    # ...and, when the description names a pad profile, to the pad it is
    # driven from, so the console's <Input> bindings are live the moment the
    # file opens rather than after somebody builds the patch by hand in the
    # Inputs/Outputs tab (input_binding.py, 2026-08-29). No pad, no input patch.
    pad = midi_pad_named(described.controllers.midi_pad)
    if pad is not None:
        pad.pin_input(workspace.root)
    # The patch carries the rig, not where any of it stands: give the 2D and 3D
    # views a plot to draw, or they stack every fixture on one spot. A workspace
    # whose Monitor already places everything was positioned by hand in QLC+ -
    # leave it alone, a generated plot is a starting point, not an improvement
    # on a measured one.
    stage_placed = 0
    if plot_path:
        stage_placed = len(
            apply_stage_plot(workspace, load_stage_plot(plot_path, workspace.root)).rigged
        )
    elif unplaced_fixtures(workspace):
        stage_placed = generate_stage_layout(workspace, library).placed
    caps = capabilities_of(workspace.root, library)
    # Wheels snap, LEDs fade: every colour, gobo and prism wheel goes into its
    # fixture's <ExcludeFade>, or the rig-wide wheel's 800 ms crossfade walks
    # the beams' colour wheel through every detent between two colours
    # (cross-audit, 2026-09-02).
    pin_wheel_fades(workspace.root, caps)

    return ShowBuild(
        workspace=workspace,
        library=library,
        vocabulary=vocabulary,
        described=described,
        wheel=wheel,
        pastels=pastels,
        contrasts=contrasts,
        beats=beats,
        pad=pad,
        stage_placed=stage_placed,
        caps=caps,
    )
