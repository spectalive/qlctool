"""The live console on the show, and the tablet desk's bursts where it has one.

Moved verbatim out of `build_canonical_show` (2026-09-26, round G).
"""

from ..control_glyph import GLYPHS
from ..is_bar import is_bar
from ..is_panel import is_panel
from ..is_smoke_machine import is_smoke_machine
from ..names.localised_keys import localised_keys
from .desk_bursts import generate_desk_bursts
from .live_console import generate_live_console
from .movement_efx import moving_head_ids
from .show_build import ShowBuild


def add_show_console(build: ShowBuild) -> list[int]:
    """Lay out the live console; the ids of every button it and the desk put up."""
    workspace = build.workspace
    library = build.library
    caps = build.caps
    vocabulary = build.vocabulary
    described = build.described
    colours = build.described.colours
    master = build.master
    beats = build.beats
    bpm_tap = build.bpm_tap
    pad = build.pad
    algorithms = build.algorithms
    banks = build.banks
    matrices = build.matrices
    movement = build.movement
    gobos = build.gobos
    beam_colors = build.beam_colors
    prisms = build.prisms
    builtins = build.builtins
    beam_subsets = build.beam_subsets
    tempo_functions = build.tempo_functions
    movement_functions = build.movement_functions
    play_wrappers = build.play_wrappers
    console = generate_live_console(
        workspace,
        master=master,
        banks=banks,
        matrices=matrices,
        movement=movement,
        gobos=gobos,
        beam_colors=beam_colors,
        prisms=prisms,
        mover_fixture_ids=moving_head_ids(workspace, library),
        builtins=builtins,
        keys=dict(described.console.keys),
        flash_functions=described.console.flash_functions,
        matrix_algorithms=[a for a in algorithms if a],
        beam_subsets=beam_subsets,
        tempo_functions=() if beats or bpm_tap else tempo_functions,
        movement_functions=() if beats or bpm_tap else movement_functions,
        bpm_tap=bpm_tap,
        play_wrappers=play_wrappers,
        colour_flash_ids=build.colour_flash_ids,
        canvas=described.console.canvas,
        tempo_beat_ms=described.timing.beat_ms,
        palette=colours.palette,
        pad_bindings=localised_keys(pad.bindings, vocabulary) if pad is not None else None,
        pad_colors=localised_keys(pad.colors, vocabulary) if pad is not None else None,
        glyphs=localised_keys(GLYPHS, vocabulary),
        vocabulary=vocabulary,
        has_bars=any(is_bar(c) for c in caps),
        has_panels=any(is_panel(c) for c in caps),
        has_smoke_machine=any(is_smoke_machine(c) for c in caps),
    )
    button_ids = console.button_ids
    if described.controllers.tablet_desk:
        button_ids.extend(generate_desk_bursts(workspace, names=vocabulary))
    return button_ids
