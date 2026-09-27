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
from typing import Any

from lxml import etree

from ..argb import argb_from_rgb
from ..control_glyph import GLYPHS
from ..names.default_names import default_names
from ..names.localised_keys import localised_keys
from ..names.names import Names
from ..palette import PALETTE
from ..vc.appearance import DEFAULT
from ..vc.audio_triggers import build_audio_triggers
from ..vc.button import FLASH, TOGGLE, build_button
from ..vc.dial_function import DialFunction
from ..vc.frame import build_frame
from ..vc.label import build_label
from ..workspace import Workspace
from .beam_subsets import GeneratedBeamSubsets
from .bind_pad import bind_pad
from .builtin_effects import GeneratedBuiltins
from .console_ids import ConsoleIds
from .console_layout import (
    AUDIO_BANDS,
    BIG_FONT,
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    MIX_COLOURS,
    OUTER_HEIGHT,
    OUTER_WIDTH,
    OUTER_X,
    OUTER_Y,
    PAGE_CONTROL,
    PAGE_NEXT_KEY,
    PAGE_PLAY,
    PAGE_PREVIOUS_KEY,
    PAGES,
    RIGHT_WIDTH,
    RIGHT_X,
    SHORT_COLOURS,
    SMALL_FONT,
    TEMPO_BEAT_MS,
    TITLE_FONT,
)
from .function_names import function_names
from .generated_bank import GeneratedBank
from .generated_console import GeneratedConsole
from .generated_matrices import GeneratedMatrices
from .generated_play_wrappers import GeneratedPlayWrappers
from .on_page import on_page
from .page_control import page_control
from .page_library import page_library
from .page_show import page_show
from .play_page import build_play_page
from .root_frame import root_frame
from .set_canvas import set_canvas
from .smc_pad_colors import readable_foreground
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

    def button(
        parent: etree._Element,
        function_id: int | None,
        caption: str,
        x: int,
        y: int,
        w: int,
        h: int,
        page: int | None = None,
        **kwargs: Any,
    ) -> etree._Element:
        widget_id = ids.take()
        element = build_button(
            parent,
            widget_id,
            caption,
            function_id,
            x=x,
            y=y,
            width=w,
            height=h,
            **kwargs,
        )
        on_page(element, page)
        console.button_ids.append(widget_id)
        console.widget_ids.append(widget_id)
        if function_id is not None:
            widget_of[function_id] = widget_id
        return element

    def frame(
        parent: etree._Element,
        caption: str,
        x: int,
        y: int,
        w: int,
        h: int,
        page: int | None = None,
        **kwargs: Any,
    ) -> etree._Element:
        widget_id = ids.take()
        element = build_frame(parent, widget_id, caption, x, y, w, h, **kwargs)
        on_page(element, page)
        console.frame_ids.append(widget_id)
        console.widget_ids.append(widget_id)
        return element

    def label(
        parent: etree._Element,
        caption: str,
        x: int,
        y: int,
        w: int,
        h: int,
        page: int | None = None,
        font: str = DEFAULT,
    ) -> etree._Element:
        widget_id = ids.take()
        element = build_label(parent, widget_id, caption, x, y, w, h, font=font)
        on_page(element, page)
        console.widget_ids.append(widget_id)
        return element

    def master_button(
        parent: etree._Element,
        name: str,
        caption: str,
        x: int,
        y: int,
        w: int,
        h: int,
        page: int | None = None,
        function_id: int | None = None,
        include_key: bool = True,
        **kwargs: Any,
    ) -> etree._Element | None:
        """A button for a master function, with its key, glyph and action."""
        target_id = function_id if function_id is not None else master.get(name)
        if target_id is None:
            return None
        # The glyph travels in the caption: QLC+'s own <Icon> is a path into the
        # show Mac's disk, and a missing file is a blank button there and
        # nowhere else (`control_glyph`, 2026-09-22).
        mark = glyphs.get(name, "")
        if mark and not caption.startswith(mark):
            caption = f"{mark} {caption}"
        # A pad-bound function wears its palette colour, so the console button
        # and the pad LED read as the same surface.
        colour = pad_colors.get(name)
        if colour is not None and "background" not in kwargs:
            kwargs["background"] = str(argb_from_rgb(colour))
            kwargs.setdefault("foreground", str(argb_from_rgb(readable_foreground(colour))))
        element = button(
            parent,
            target_id,
            caption,
            x,
            y,
            w,
            h,
            page=page,
            key=keys.get(name) if include_key else None,
            action=FLASH if name in flash else TOGGLE,
            # A hit must read over the running state, not merely join it.
            # Override only orders the faders: on an HTP channel the level's
            # higher value still wins the compare, so a MiN Wash strobe on its
            # Intensity-group Dimmer/Strobe channel never showed under a level
            # (`rule_strobe_masked_by_htp`, 2026-09-26). ForceLTP writes past it.
            flash_override=name in flash,
            flash_force_ltp=name in flash,
            **kwargs,
        )
        bind_pad(element, pad_bindings, name)
        return element

    outer = frame(
        console_root,
        "",
        OUTER_X,
        OUTER_Y,
        OUTER_WIDTH,
        OUTER_HEIGHT,
        pages=PAGES,
        next_page_key=PAGE_NEXT_KEY,
        previous_page_key=PAGE_PREVIOUS_KEY,
        font=TITLE_FONT,
    )
    # When a pad profile is given, its arrow buttons page the console: a
    # frame's Next Page is external control 0 and Previous Page is 1 (qmlui
    # vcframe.h). Without a pad, nothing is bound.
    bind_pad(outer, pad_bindings, vocabulary.display("page_next"))
    bind_pad(outer, pad_bindings, vocabulary.display("page_previous"), source_id=1)

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
