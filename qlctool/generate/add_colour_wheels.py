"""The rig-wide colour wheels: full, multicolour, simple, pastel and mix.

Moved verbatim out of `build_canonical_show` (2026-09-26, round G); the
functions are created in the order they always were.
"""

from ..functions.chaser import build_chaser
from ..ids import next_function_id
from .multicolor_scene import generate_multicolor_scenes
from .quad_color_scenes import generate_quad_color_scenes
from .show_build import ShowBuild
from .show_collection import show_collection
from .unison_colors import WHEEL_FADE, WHEEL_HOLD, generate_unison_colors
from .wheel_colors_of import wheel_colors_of


def add_colour_wheels(build: ShowBuild) -> None:
    """The four automatic colour modes and the mix wheel."""
    workspace = build.workspace
    library = build.library
    vocabulary = build.vocabulary
    wheel = build.wheel
    pastels = build.pastels
    contrasts = build.contrasts
    master = build.master
    builtins = build.builtins
    banks = build.banks
    matrix_lit_ids = build.matrix_lit_ids
    step_matrices = build.step_matrices
    pastel_step_matrices = build.pastel_step_matrices
    colours = build.described.colours
    # One wheel over the whole rig, not one per group: three Random wheels
    # never land on the same colour, and the heads and the PARs have to.
    # Off the rig-wide wheel go the fixtures somebody else is colouring: the
    # pixel groups their matrix paints, and the panels running their own
    # programmes, which ignore red, green and blue while they do.
    # The panels whose RGB the wheel writes without touching their mode: the
    # self-animating ones - minus any a matrix already paints, because a
    # fixture gets one colour source and a matrix-painted panel already has
    # its own (the old DeluxeEventos2 patch kept two of them inside the bars'
    # group, and that patch still builds).
    program_gated = sorted(set(builtins.fixture_ids) - matrix_lit_ids)
    # The wild steps: every fixture its own colour. Until 2026-09-22 they were
    # ordinary steps of the rig wheel, so "de vez en cuando" was the Random
    # rotation doing its job - and what the room got was a fair ("los colores
    # siguen siendo una feria", owner). They are a wheel of their own now,
    # `Rueda Multicolor`, that no state starts: "solo por si acaso".
    multicolor_ids = generate_multicolor_scenes(
        workspace,
        library,
        colors=list(wheel_colors_of(wheel, contrasts).items()),
        exclude_fixture_ids=sorted(matrix_lit_ids),
        program_gated_ids=program_gated,
        names=vocabulary,
    )
    # The hand-built "4 Colores" rotations, back beside the wild steps: the
    # same deal of blue/red/green/white walked one seat per scene.
    quad_ids = generate_quad_color_scenes(
        workspace,
        library,
        exclude_fixture_ids=sorted(matrix_lit_ids),
        program_gated_ids=program_gated,
        palette=colours.palette,
        names=vocabulary,
    )
    # The wild steps: every fixture its own colour. The Plasma Rainbow matrices
    # that used to slide a whole gradient across the bars beside them are gone -
    # "quitar multicolores muy feos" (owner, 2026-09-22), and they were the one
    # look that guaranteed a colour hit landing on a bar already mixed towards
    # white. The pixel groups still need a colour while a wild step runs, since
    # the scene excludes them (one fixture, one colour source), so each step
    # takes the plain matrices of one palette colour, walked so consecutive
    # steps differ.
    wild_scenes = [
        (scene_id, vocabulary.render("rig_multicolour", number=n))
        for n, scene_id in enumerate(multicolor_ids, start=1)
    ] + [
        (scene_id, vocabulary.render("rig_four_colours", number=n))
        for n, scene_id in enumerate(quad_ids, start=1)
    ]
    wild_palette = list(step_matrices)
    multicolor_steps = []
    for index, (scene_id, step_name) in enumerate(wild_scenes):
        extras = step_matrices[wild_palette[index % len(wild_palette)]] if wild_palette else []
        multicolor_steps.append(
            show_collection(
                workspace, vocabulary.render("with_pixels", name=step_name), [scene_id, *extras]
            )
            if extras
            else scene_id
        )
    # Four automatic colour modes, one clock each and only one ever running:
    # "modos auto deberia tener solo colores simples, colores completos,
    # colores pastel tenues" (owner, 2026-09-22), plus the multicolour wheel
    # the same evening. AUTO starts the full one; the console's buttons share
    # a solo frame, so choosing one stops the others and the room keeps
    # exactly one colour source. None of them steps white: "luz blanca solo
    # para blanco total" (`wheel_palette`, `rule_wheel_white`), and none a
    # state runs puts more than two colours on the room at once
    # (`rule_state_palette`).
    excluded_from_wheel = sorted(matrix_lit_ids | set(builtins.fixture_ids))
    unison = generate_unison_colors(
        workspace,
        library,
        colors=tuple(wheel),
        exclude_fixture_ids=excluded_from_wheel,
        step_extras=step_matrices,
        program_gated_ids=program_gated,
        contrasts=contrasts,
        palette=dict(colours.palette),
        names=vocabulary,
    )
    if unison.wheel_id is not None:
        master[vocabulary.display("colour_wheel")] = unison.wheel_id
    if multicolor_steps:
        multicolor_wheel_id = next_function_id(workspace.root)
        workspace.add_function(
            build_chaser(
                multicolor_wheel_id,
                vocabulary.display("multicolour_wheel"),
                multicolor_steps,
                fade_in=WHEEL_FADE,
                hold=WHEEL_HOLD,
                fade_out=WHEEL_FADE,
                run_order="Random",
                path=vocabulary.display("path_rig_colours"),
            )
        )
        master[vocabulary.display("multicolour_wheel")] = multicolor_wheel_id
    # The plain mode: the six primaries, one at a time, no contrasts and none
    # of the wild multicolour steps.
    simples = generate_unison_colors(
        workspace,
        library,
        colors=colours.simple,
        contrasts=(),
        exclude_fixture_ids=excluded_from_wheel,
        step_extras=step_matrices,
        program_gated_ids=program_gated,
        wheel_name=vocabulary.display("simple_wheel"),
        scene_prefix=vocabulary.display("rig_prefix_simple"),
        palette=dict(colours.palette),
        names=vocabulary,
    )
    if simples.wheel_id is not None:
        master[vocabulary.display("simple_wheel")] = simples.wheel_id
    pasteles = generate_unison_colors(
        workspace,
        library,
        colors=tuple(pastels),
        contrasts=(),
        exclude_fixture_ids=excluded_from_wheel,
        step_extras=pastel_step_matrices,
        program_gated_ids=program_gated,
        palette=pastels,
        wheel_name=vocabulary.display("pastel_wheel"),
        scene_prefix=vocabulary.display("rig_prefix_pastel"),
        names=vocabulary,
    )
    if pasteles.wheel_id is not None:
        master[vocabulary.display("pastel_wheel")] = pasteles.wheel_id
    master[vocabulary.display("mix_wheel")] = show_collection(
        workspace,
        vocabulary.display("mix_wheel"),
        [b.mix_wheel_id for b in banks if b.mix_wheel_id is not None],
    )
    build.unison = unison
