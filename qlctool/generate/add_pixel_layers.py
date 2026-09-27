"""The matrices, the pixel groups' intensity and the matrices the colour wheels start.

Moved verbatim out of `build_canonical_show` (2026-09-26, round G); the
functions are created in the order they always were.
"""

from .. import roles
from ..fixture_group import fixture_groups
from ..rgb_cells import rgb_cells
from ..rigged_fixture_ids import rigged_fixture_ids
from .all_self_animating import all_self_animating
from .beam_rainbow_spin import generate_beam_rainbow_spin
from .build_refusal_error import BuildRefusalError
from .cycle_algorithms import CYCLE_ALGORITHMS
from .generate_matrix_effects import generate_matrix_effects
from .generated_matrices import GeneratedMatrices
from .is_pixel_group import is_pixel_group
from .panel_manual import generate_panel_manual
from .pixel_base import generate_pixel_base
from .pixel_wheel_matrices import generate_pixel_wheel_matrices
from .show_build import ShowBuild
from .wheel_colors_of import wheel_colors_of


def add_pixel_layers(build: ShowBuild) -> None:
    """Matrices per group, the pixel groups' own layer and the wheels' step matrices."""
    workspace = build.workspace
    caps = build.caps
    vocabulary = build.vocabulary
    described = build.described
    wheel = build.wheel
    pastels = build.pastels
    contrasts = build.contrasts
    master = build.master
    algorithms = build.algorithms
    matrix_colors = build.matrix_colors
    builtins = build.builtins
    panel_cycle_id = build.panel_cycle_id
    colours = build.described.colours
    matrices: list[GeneratedMatrices] = []
    # Matrices are drawn only where a group is really made of pixels: on a
    # group of single-cell fixtures a matrix is a colour wheel with extra
    # steps. The pixel groups' colour, though, belongs to the rig-wide wheel -
    # their matrices ride inside its steps, one per wheel colour, because two
    # chasers each rotating colour on their own clock never agree: the wheel
    # had the room on cyan while the bars' cycle had them on magenta ("van con
    # los colores a su bola", owner, 2026-08-26). The standalone cycle is still
    # generated for the console; AUTO does not step it.
    pixel_group_ids: list[int] = []
    # Every fixture a running matrix paints. The rig-wide colour wheel is kept
    # off these: RGB mixes HTP, so a bar told red by the wheel and blue by its
    # matrix comes out magenta, and a third source makes it white. One fixture,
    # one colour source.
    matrix_lit_ids: set[int] = set()
    # The wheel-coloured fixtures' answer to a hue that travels, generated
    # before the looks that need it: a matrix cycle and both rainbows run it
    # beside themselves so the beams sweep colour with the room instead of
    # holding one detent (`rule_colour_animation_wheel`, 2026-09-22).
    beam_spin_id = generate_beam_rainbow_spin(workspace, caps, names=vocabulary)
    subset = {
        name: colours.palette[name]
        for name in (colours.matrix_colors if matrix_colors is None else matrix_colors)
    }
    by_id = {capability.fixture.fixture_id: capability for capability in caps}
    rigged = rigged_fixture_ids(workspace.root)
    for group in fixture_groups(workspace.root):
        # A fixture with forty-two animations of its own does not need a
        # four-cell chase drawn over it, and could not show one anyway: in its
        # automatic mode it ignores the red, green and blue a matrix writes.
        if all_self_animating(caps, group.fixture_ids):
            continue
        # Nor is a matrix drawn where no rigged cell has red, green and blue:
        # `Cabezas` was 7R beams on a colour wheel and spares in a flight
        # case, and its matrices lit nothing anybody saw (ruling D6,
        # 2026-09-26). A matrix the description asks for there is refused.
        if not rigged.intersection(rgb_cells(by_id, group.fixture_ids)):
            if described.matrices.get(group.name):
                raise BuildRefusalError(vocabulary.render("invisible_matrices", group=group.name))
            continue
        generated = generate_matrix_effects(
            workspace,
            group_id=group.group_id,
            algorithms=algorithms,
            chaser_algorithms=CYCLE_ALGORITHMS,
            palette=subset,
            path=vocabulary.render("matrices_of", group=group.name),
            curated=list(described.matrices.get(group.name, ())),
            curated_palette=colours.palette,
            names=vocabulary,
        )
        matrices.append(generated)
        if generated.chaser_id is not None and is_pixel_group(caps, group.fixture_ids):
            pixel_group_ids.append(group.group_id)
            matrix_lit_ids |= set(group.fixture_ids)
    matrix_ids = [fid for m in matrices for fid in m.matrix_ids]

    # A matrix writes RGB and nothing else, so the panels' master dimmer and
    # shutter need somebody. That used to be the rig-wide wheel, until these
    # fixtures were taken off it; without this they are coloured and dark.
    pixel_base_id = generate_pixel_base(
        workspace,
        caps,
        sorted(matrix_lit_ids),
        exclude_effect_mode_fixture_ids=builtins.fixture_ids,
        names=vocabulary,
    )
    if pixel_base_id is not None:
        master[vocabulary.display("pixels_on")] = pixel_base_id
    charla_pixel_intensity_id = generate_pixel_base(
        workspace,
        caps,
        sorted(matrix_lit_ids | set(builtins.fixture_ids)),
        name=vocabulary.display("talk_pixel_intensity"),
        path=vocabulary.display("path_moments"),
        include_effect_mode=False,
        names=vocabulary,
    )
    paneles_charla_id = generate_panel_manual(
        workspace,
        caps,
        builtins.fixture_ids,
        name=vocabulary.display("talk_panels"),
        path=vocabulary.display("path_moments"),
        include_intensity=False,
        names=vocabulary,
    )
    # Everything the pixel groups need beside the wheel: their intensity, and
    # the panels' own programmes. Their colour is not here - the wheel's steps
    # carry it, matrix included. Wherever the wheel goes, this goes.
    pixel_layer = [fid for fid in (pixel_base_id, panel_cycle_id) if fid is not None]

    # The wheel colours the pixel groups too, but through a matrix of its own
    # colour started by each step - never through the scene, whose RGB would
    # mix HTP with the matrix and land on a colour nobody chose. The steps
    # exist only where the rig wheel has a fixture to colour outside the
    # pixel groups; on a rig that is all pixels the per-group wheels are the
    # colour source and these matrices started nothing (`unreachable_function`,
    # 2026-09-27).
    wheel_lit = any(
        (c.has_role(roles.RED) or c.has_role(roles.COLOR_MACRO))
        and c.fixture.fixture_id not in matrix_lit_ids
        for c in caps
    )
    step_matrices = (
        generate_pixel_wheel_matrices(
            workspace,
            pixel_group_ids,
            wheel_colors_of(wheel, contrasts),
            CYCLE_ALGORITHMS,
            names=vocabulary,
        )
        if pixel_group_ids and wheel_lit
        else {}
    )
    # And the same for the pastel mode, whose colours are the same names with
    # less of each: the pixel groups follow whichever wheel is running.
    pastel_step_matrices = (
        generate_pixel_wheel_matrices(
            workspace,
            pixel_group_ids,
            {name: pastels[name] for name in wheel_colors_of(wheel, contrasts)},
            CYCLE_ALGORITHMS,
            tag=vocabulary.display("pastel_wheel"),
            names=vocabulary,
        )
        if pixel_group_ids and wheel_lit
        else {}
    )
    build.beam_spin_id = beam_spin_id
    build.matrices = matrices
    build.matrix_lit_ids = matrix_lit_ids
    build.matrix_ids = matrix_ids
    build.charla_pixel_intensity_id = charla_pixel_intensity_id
    build.paneles_charla_id = paneles_charla_id
    build.pixel_layer = pixel_layer
    build.step_matrices = step_matrices
    build.pastel_step_matrices = pastel_step_matrices
