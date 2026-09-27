"""Lay out the console the show is run from: four pages, biggest first.

The person in front of this laptop is not a lighting operator. They are whoever
is nearest when something happens, on a 13" screen, in a dark room, with a party
going on - so the console is built to a fixed 1440x900 and split into four
pages that answer four different questions:

1. **Show** - what state is the room in, and how do I hit it? Seven big buttons
   for the state and six for the hits that ride on top. Nothing else.
2. **Jugar** - family-scoped picks that release when the show's owner returns.
3. **Control** - direct fixture banks, aiming, intensity, speed and smoke.
4. **Libreria** - the raw material the show is built from: 90 two-colour mixes,
   100 matrix effects, 20 gobos, 17 beam colours. Nobody hunts through these
   mid-set; they are here to be borrowed, not pressed.

Two rules decide the frames.

**A function and the functions it starts never share a solo frame.** A solo
frame stops every other widget's function as soon as one starts
(qmlui's `VCSoloFrame::slotFunctionStarting`), and a Toggle button reports its
function starting however it was started - so AUTO dies the instant it starts a
wheel that sits in the same solo frame. Masters and anything that drives other
functions live in plain frames; only leaf looks are grouped solo.

**The room is in exactly one state.** That is the same mechanism used
deliberately: AUTO, the four moments, the work light and the blackout share one
solo frame, so starting any of them stops whichever was running. That is what
makes "Ambiente and Fiesta at the same time" - two energy levels stacked on one
rig, which is what turned the room white - impossible to press.
"""

from collections.abc import Mapping, Sequence

from ..control_glyph import GLYPHS
from ..names.default_names import default_names
from ..names.localised_keys import localised_keys
from ..names.names import Names
from ..palette import PALETTE
from ..vc.audio_triggers import build_audio_triggers
from ..vc.dial_function import DialFunction
from ..workspace import Workspace
from .beam_subsets import GeneratedBeamSubsets
from .builtin_effects import GeneratedBuiltins
from .button_factory import button_factory
from .console_ids import ConsoleIds
from .console_layout import (
    AUDIO_BANDS,
    BIG_FONT,
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    MIX_COLOURS,
    PAGE_CONTROL,
    PAGE_PLAY,
    RIGHT_WIDTH,
    RIGHT_X,
    SHORT_COLOURS,
    SMALL_FONT,
    TEMPO_BEAT_MS,
    TITLE_FONT,
)
from .console_outer_frame import console_outer_frame
from .frame_factory import frame_factory
from .function_names import function_names
from .generated_bank import GeneratedBank
from .generated_console import GeneratedConsole
from .generated_matrices import GeneratedMatrices
from .generated_play_wrappers import GeneratedPlayWrappers
from .label_factory import label_factory
from .master_button_factory import master_button_factory
from .on_page import on_page
from .page_control import page_control
from .page_library import page_library
from .page_show import page_show
from .play_page import build_play_page
from .root_frame import root_frame
from .set_canvas import set_canvas
from .wheel_scenes import GeneratedWheel


def generate_live_console(
    workspace: Workspace,
    master: dict[str, int],
    banks: Sequence[GeneratedBank],
    matrices: Sequence[GeneratedMatrices],
    beam_colors: GeneratedWheel,
    mover_fixture_ids: Sequence[int],
    builtins: GeneratedBuiltins,
    keys: dict[str, str],
    flash_functions: Sequence[str] = (),
    matrix_algorithms: Sequence[str] = (),
    beam_subsets: GeneratedBeamSubsets | None = None,
    tempo_functions: Sequence[DialFunction] = (),
    movement_functions: Sequence[DialFunction] = (),
    bpm_tap: bool = False,
    play_wrappers: GeneratedPlayWrappers | None = None,
    colour_flash_ids: dict[str, int] | None = None,
    canvas: tuple[int, int] = (CANVAS_WIDTH, CANVAS_HEIGHT),
    tempo_beat_ms: int = TEMPO_BEAT_MS,
    palette: Mapping[str, tuple[int, int, int]] | None = None,
    pad_bindings: Mapping[str, int] | None = None,
    pad_colors: Mapping[str, tuple[int, int, int]] | None = None,
    glyphs: Mapping[str, str] | None = None,
    vocabulary: Names | None = None,
    *,
    has_bars: bool = False,
    has_panels: bool = False,
    has_smoke_machine: bool,
) -> GeneratedConsole:
    """Build the whole console on the workspace's (emptied) root frame.

    `pad_bindings`, `pad_colors` and `glyphs` are keyed by display name;
    `glyphs=None` means the shipped glyphs in the vocabulary. The console's
    words come from `vocabulary`; None means `default_names()`.
    `has_bars` and `has_panels` say some patched fixture is a bar
    (`is_bar`) or a panel (`is_panel`): page 4's captions name only those. `has_smoke_machine` says a
    smoke or haze machine is patched: page 3's title promises haze only then.
    """
    vocabulary = default_names() if vocabulary is None else vocabulary
    pad_bindings = dict(pad_bindings or {})
    pad_colors = dict(pad_colors or {})
    glyphs = localised_keys(GLYPHS, vocabulary) if glyphs is None else dict(glyphs)
    # The short forms the bank and mix buttons wear, keyed by colour name.
    short_colour = {vocabulary.display(c): vocabulary.display(f"{c}_short") for c in SHORT_COLOURS}
    mix_code = {vocabulary.display(c): vocabulary.display(f"{c}_code") for c in MIX_COLOURS}
    colours = PALETTE if palette is None else palette
    console_root = root_frame(workspace.root)
    names = function_names(workspace)
    ids = ConsoleIds(workspace.root)
    console = GeneratedConsole()
    flash = set(flash_functions)

    widget_of: dict[int, int] = {}
    button = button_factory(ids, console, widget_of)
    frame = frame_factory(ids, console)
    label = label_factory(ids, console)
    master_button = master_button_factory(
        button, master, keys, flash, glyphs, pad_colors, pad_bindings
    )

    outer = console_outer_frame(console_root, frame, pad_bindings, vocabulary)

    page_show(
        outer,
        button,
        master_button,
        frame,
        label,
        ids,
        console,
        master,
        tempo_functions,
        bpm_tap,
        tempo_beat_ms,
        pad_bindings,
        vocabulary,
    )
    if play_wrappers is not None:
        build_play_page(
            outer,
            button,
            master_button,
            frame,
            label,
            names,
            master,
            play_wrappers,
            colour_flash_ids or {},
            flash_functions,
            PAGE_PLAY,
            TITLE_FONT,
            BIG_FONT,
            SMALL_FONT,
            palette=colours,
            vocabulary=vocabulary,
        )
    page_control(
        outer,
        button,
        master_button,
        frame,
        label,
        ids,
        console,
        names,
        banks,
        beam_colors,
        master,
        mover_fixture_ids,
        movement_functions,
        tempo_beat_ms,
        colours,
        pad_bindings,
        vocabulary,
        short_colour,
        mix_code,
        has_smoke_machine,
    )
    page_library(
        outer,
        button,
        master_button,
        frame,
        label,
        ids,
        console,
        names,
        banks,
        matrices,
        builtins,
        matrix_algorithms,
        beam_subsets,
        colours,
        vocabulary,
        mix_code,
        has_bars,
        has_panels,
    )

    # Last, because a band presses a button and needs its widget ID.
    bars: list[tuple[str, int | None]] = []
    for band, target in AUDIO_BANDS:
        pressed = master.get(vocabulary.display(target)) if target else None
        bars.append(
            (vocabulary.display(band), widget_of.get(pressed) if pressed is not None else None)
        )
    triggers_id = ids.take()
    triggers = build_audio_triggers(
        outer,
        triggers_id,
        vocabulary.display("audio_triggers"),
        RIGHT_X,
        330,
        RIGHT_WIDTH,
        110,
        bars=bars,
    )
    on_page(triggers, PAGE_CONTROL)
    console.widget_ids.append(triggers_id)

    set_canvas(workspace.root, canvas)
    return console
