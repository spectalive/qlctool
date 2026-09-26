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
from dataclasses import dataclass, field

from lxml import etree

from ..argb import argb_from_rgb
from ..control_glyph import GLYPHS
from ..names.default_names import default_names
from ..names.localised_keys import localised_keys
from ..names.names import Names
from ..names.template_affixes import template_affixes
from ..palette import PALETTE
from ..vc.appearance import DEFAULT
from ..vc.audio_triggers import build_audio_triggers
from ..vc.bank_pitch import (
    BANK_COLUMN_TOP,
    DIMMER_FRAME_HEIGHT,
    bank_pitch_for,
)
from ..vc.button import BLACKOUT, FLASH, STOP_ALL, TOGGLE, build_button
from ..vc.console_font import console_font
from ..vc.dial_function import DialFunction
from ..vc.frame import build_frame
from ..vc.grand_master_slider import build_grand_master_slider
from ..vc.label import build_label
from ..vc.level_slider import build_level_slider
from ..vc.matrix_control import build_matrix_control
from ..vc.speed_dial import build_speed_dial
from ..vc.widget_ids import next_widget_id
from ..vc.xy_pad import build_xy_pad
from ..workspace import Workspace
from ..xmlutil import find_local, localname
from .bind_pad import bind_pad
from .library_help_lines import library_help_lines
from .matrices_frame_caption import matrices_frame_caption
from .page_control_title import page_control_title
from .panels_frame_caption import panels_frame_caption
from .play_page import build_play_page
from .smc_pad_colors import readable_foreground
from .tempo_close_line import tempo_close_line
from .tempo_help_line import tempo_help_line

CANVAS_WIDTH = 1440
CANVAS_HEIGHT = 900
HEADER = 26  # the frame header, where the page arrows live
GAP = 6

# The console is one multipage frame filling the screen. The page arrows are in
# its header; these keys do the same without aiming a mouse in the dark.
PAGE_NEXT_KEY = "PgDown"
PAGE_PREVIOUS_KEY = "PgUp"
PAGE_SHOW, PAGE_PLAY, PAGE_CONTROL, PAGE_LIBRARY = 0, 1, 2, 3
PAGES = 4

# The panic button. Backspace because it is big, reachable without looking, and
# bound to nothing else in QLC+ or in this console.
STOP_ALL_KEY = "Backspace"
STOP_ALL_FADE_MS = 1000
# Escape, for the same reason - free everywhere else on this console.
BLACKOUT_KEY = "Escape"

OUTER_X, OUTER_Y = 4, 4
OUTER_WIDTH, OUTER_HEIGHT = 1432, 892

LEFT_X, LEFT_WIDTH = 8, 524
MIDDLE_X, MIDDLE_WIDTH = 540, 628
RIGHT_X, RIGHT_WIDTH = 1176, 256

TITLE_FONT = console_font(15)
HUGE_FONT = console_font(28)
BIG_FONT = console_font(15)
HELP_FONT = console_font(11, bold=False)
# A colour bank button is 48px wide and a mix button carries two names: at the
# console's own size the caption is cut off, and a cut-off caption is what the
# blank buttons it replaces were.
SMALL_FONT = console_font(9)
TINY_FONT = console_font(8)

# The library's Matrices frame: the recovered algorithm families (old-vs-new
# audit, 2026-08-28) push the widest group (BarrasLed) to 43 buttons (30 base
# + 13 curated). Eight columns at 40px rows fit 48 in the frame's 300px height
# (24px group label + 6 rows), so the frame still does not grow into the
# "Ruedas y ciclos" frame below it.
MATRIX_COLUMNS = 8
MATRIX_ROW_HEIGHT = 40
MATRIX_BUTTON_HEIGHT = 36

# Keys 1-0 across a colour bank, as the hand-built console has them. Every
# widget sees every key press - on any page, visible or not - so one key lights
# that colour on all three banks.
BANK_KEYS = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")

# A colour bank button is 44px wide: the name has to survive that. Each
# colour's short form is the catalogue's `<colour>_short`.
SHORT_COLOURS = ("ultraviolet", "yellow", "magenta", "white", "orange")
# ...and a two-colour mix carries two of them, so those go to two letters
# (`<colour>_code`). One letter is what made "R/A" mean both Rojo/Azul and
# Rojo/Amarillo; Ambar joined the mixes on 2026-09-22 and shares Amarillo's
# first two letters, the same trap as Azul.
MIX_COLOURS = (
    "red",
    "green",
    "blue",
    "yellow",
    "amber",
    "cyan",
    "magenta",
    "white",
    "orange",
    "pink",
    "ultraviolet",
)
# Two wheel positions carry a sentence for a name and no button is that wide.
# The keys are fixture-definition data; the values are catalogue identifiers.
LONG_WHEEL_NAME = {
    "Rainbow effect fast to slow": "rainbow_plus",
    "Rainbow effect reverse slow to fast": "rainbow_minus",
}

# The room's state: one at a time, biggest first. Function identifier,
# caption identifier, and the geometry inside the solo frame.
ROOM_STATES: tuple[tuple[str, str, tuple[int, int, int, int], str], ...] = (
    ("auto", "room_auto", (8, 26, 690, 190), HUGE_FONT),
    ("talk_moment", "room_talk", (704, 26, 352, 92), BIG_FONT),
    ("calm_moment", "room_calm", (1062, 26, 352, 92), BIG_FONT),
    ("party_moment", "room_party", (704, 124, 352, 92), BIG_FONT),
    ("frenzy_moment", "room_frenzy", (1062, 124, 352, 92), BIG_FONT),
    ("full_white", "room_white", (8, 222, 690, 92), BIG_FONT),
    ("all_black", "room_black", (704, 222, 710, 92), BIG_FONT),
)

# The hits: they add to whatever state is running instead of replacing it, so
# they live in a plain frame. Six across one row. (function, caption) identifiers.
HITS: tuple[tuple[str, str], ...] = (
    ("flash_full", "hit_button_flash"),
    ("flash_half", "hit_button_flash_slow"),
    ("flash_colour", "hit_button_flash_colour"),
    ("smoke_on", "hit_button_smoke_now"),
    ("vertical_smoke_now", "hit_button_vertical_smoke_now"),
    ("strobe_fast", "hit_button_strobe"),
    ("strobe_medium", "hit_button_strobe_soft"),
)

# What page 1 says about itself, because nobody reads a manual at a venue.
HELP_LINES = ("help_show_1", "help_show_2", "help_show_3", "help_show_4", "help_show_5")
# The lines that speak of the haze, and what each says on a show without one:
# "AUTO is colours, haze and ..." and "HAZE NOW works while held" are false on
# a rig with no haze machine (2026-09-25, Plan C preflight D9).
HELP_WITHOUT_HAZE = {
    "help_show_1": "help_show_1_no_haze",
    "help_show_3": "help_show_3_no_haze",
}

HELP_ROW_Y = 630
# The haze row was 28px tall under SMALL_FONT while every other button on the
# page was 92 or 118 under BIG_FONT: "botones de humo pequeños comparados con el
# resto" (owner, 2026-09-22). Page 1 had 86px of dead space between the room
# states and the hits, which is what pays for this.
SMOKE_ROW_Y = 770
SMOKE_ROW_HEIGHT = 110
SMOKE_BUTTON_HEIGHT = 74
# The haze rhythms, under the help text on page 1. The captions say minutes
# because that is the question being asked - "cada cuanto" - and the first one
# carries the key the hand-built console had on the haze.
# (function, caption) identifiers.
SMOKE_RHYTHMS: tuple[tuple[str, str], ...] = (
    ("smoke_auto", "haze_every_1"),
    ("smoke_auto_2_min", "haze_every_2"),
    ("smoke_auto_4_min", "haze_every_4"),
    ("smoke_auto_8_min", "haze_every_8"),
)

# The tempo dial lives on page 1 since 2026-08-29: the owner taps the room's
# tempo often enough that it belongs where the operator is looking, on the
# hand-built console's tap key. Its time is one beat and every layer under it
# carries its own multiplier, so a tap moves them all and none of them loses
# its shape - the "se vuelven todos los programas locos" the owner reported
# was one dial writing the same raw interval into every wheel.
#
# The head movement gets a dial of its own, on page 3 and on the SAME tap key
# (a key press reaches every widget bound to it - VCPage::handleKeyEvent walks
# all matches - which is how the hand-built console had one M for three
# dials). It is separate because its numbers are: a shape is sixteen taps
# where a colour is eight, and its EFX have to be re-timed alongside their
# chaser or the figure stops being a proportion of the step.
TEMPO_TAP_KEY = "M"
TEMPO_BEAT_MS = 500  # the dial's starting beat: 120 BPM
MOVEMENT_DIAL_LINES = ("movement_dial_1", "movement_dial_2", "movement_dial_3")

# The workspace's own GrandMaster - it scales every output - had no widget
# bound to it at all. It wants to sit below "Intensidad y strobo de
# fixture", the only other widget that touches every fixture instead of one
# function, but the left column's colour banks grow with the rig - four
# groups already leave that spot off the bottom of a 900px screen - so it
# sits under the audio triggers on the right instead, where there is room.
GRAND_MASTER_WIDTH = 90
GRAND_MASTER_HEIGHT = 140
GRAND_MASTER_LINES = (
    "grand_master_1",
    "grand_master_2",
    "grand_master_3",
    "grand_master_4",
    "grand_master_5",
)

# Page 3's intensity chases and the fixture strobe, three across two rows.
# (function, caption) identifiers.
DIMMER_CHASES: tuple[tuple[str, str], ...] = (
    ("dimmer_chase", "chase_sweep"),
    ("dimmer_chase_2", "chase_reverse"),
    ("dimmer_pingpong", "chase_odd_even"),
    ("dimmer_sequence", "chase_rotation"),
    ("strobe_on", "chase_strobe_on"),
    ("strobe_off", "chase_strobe_off"),
)

# Page 4 says what it is for, because a page of 180 buttons otherwise reads as
# something somebody is supposed to be using; `library_help_lines` picks the
# lines. The "· · ·" separators are not words (ruling B6) and stay literal.
LIBRARY_SEPARATOR = "· · ·"

# The five spectrum bands. The strobe was wired to the upper mids until
# 2026-08-27: a strobe fired by whatever the PA does is a strobe nobody
# chose, and the safety cap on flash rate means nothing if a cymbal can hold
# the button - so no band reaches one (`disparador de audio vacio` checks
# that on every function the bound bars can reach, not just this one).
# Bass is bound to `Golpe Graves`, the plain white twin of the flash: a
# Scene, Flash action with override priority, in no solo frame. An audio bar
# presses on the way up and releases on the way down exactly the way
# `VCButton::pressFunction`/`releaseFunction` expect a Flash button to be
# worked, so the bass gets a momentary white hit that lets go on its own. It
# was `Blanco Total` first (shares the AUTO solo frame: the bass stopped
# AUTO), then `Flash 100%` - until that scene got its hardware strobe back,
# and a strobe fired by whatever the PA does is a strobe nobody chose.
AUDIO_BANDS: tuple[tuple[str, str | None], ...] = (
    ("band_bass", "bass_hit"),
    ("band_low_mid", None),
    ("band_mid", None),
    ("band_high_mid", None),
    ("band_high", None),
)


@dataclass(frozen=True)
class GeneratedConsole:
    frame_ids: list[int] = field(default_factory=list)
    button_ids: list[int] = field(default_factory=list)
    widget_ids: list[int] = field(default_factory=list)


class _Ids:
    """Widget IDs, handed out in order from wherever the console left off."""

    def __init__(self, root: etree._Element) -> None:
        self._next = next_widget_id(root)

    def take(self) -> int:
        value = self._next
        self._next += 1
        return value


def generate_live_console(
    workspace: Workspace,
    master: dict[str, int],
    banks: Sequence,
    matrices: Sequence,
    movement,
    gobos,
    beam_colors,
    prisms,
    mover_fixture_ids: Sequence[int],
    builtins,
    keys: dict[str, str],
    flash_functions: Sequence[str] = (),
    matrix_algorithms: Sequence[str] = (),
    beam_subsets=None,
    tempo_functions: Sequence[DialFunction] = (),
    movement_functions: Sequence[DialFunction] = (),
    bpm_tap: bool = False,
    play_wrappers=None,
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
    root_frame = _root_frame(workspace.root)
    names = _function_names(workspace)
    ids = _Ids(workspace.root)
    console = GeneratedConsole()
    flash = set(flash_functions)

    widget_of: dict[int, int] = {}

    def button(parent, function_id, caption, x, y, w, h, page=None, **kwargs):
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
        _on_page(element, page)
        console.button_ids.append(widget_id)
        console.widget_ids.append(widget_id)
        if function_id is not None:
            widget_of[function_id] = widget_id
        return element

    def frame(parent, caption, x, y, w, h, page=None, **kwargs):
        widget_id = ids.take()
        element = build_frame(parent, widget_id, caption, x, y, w, h, **kwargs)
        _on_page(element, page)
        console.frame_ids.append(widget_id)
        console.widget_ids.append(widget_id)
        return element

    def label(parent, caption, x, y, w, h, page=None, font=DEFAULT):
        widget_id = ids.take()
        element = build_label(parent, widget_id, caption, x, y, w, h, font=font)
        _on_page(element, page)
        console.widget_ids.append(widget_id)
        return element

    def master_button(
        parent,
        name,
        caption,
        x,
        y,
        w,
        h,
        page=None,
        function_id=None,
        include_key=True,
        **kwargs,
    ):
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
            # A hit must read over the running state, not merely join it:
            # without override priority a white flash is one more HTP bid.
            flash_override=name in flash,
            **kwargs,
        )
        bind_pad(element, pad_bindings, name)
        return element

    outer = frame(
        root_frame,
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

    _page_show(
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
    _page_control(
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
    _page_library(
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
    triggers_id = ids.take()
    triggers = build_audio_triggers(
        outer,
        triggers_id,
        vocabulary.display("audio_triggers"),
        RIGHT_X,
        330,
        RIGHT_WIDTH,
        110,
        bars=[
            (
                vocabulary.display(band),
                widget_of.get(master.get(vocabulary.display(target))) if target else None,
            )
            for band, target in AUDIO_BANDS
        ],
    )
    _on_page(triggers, PAGE_CONTROL)
    console.widget_ids.append(triggers_id)

    _set_canvas(workspace.root, canvas)
    return console


def _page_show(
    outer,
    button,
    master_button,
    frame,
    label,
    ids,
    console,
    master: Mapping[str, int],
    tempo_functions,
    bpm_tap,
    tempo_beat_ms,
    pad_bindings: Mapping[str, int],
    vocabulary: Names,
) -> None:
    """Page 1: the state the room is in, the hits, and the panic button."""
    # The show hazes when the haze timer was built: its functions are in the
    # master, as `canonical_show` puts them only for a fog-only machine.
    hazes = any(
        master.get(vocabulary.display(function)) is not None
        for function in ("smoke_on", *(f for f, _ in SMOKE_RHYTHMS))
    )
    label(
        outer,
        vocabulary.display("page_show"),
        LEFT_X,
        30,
        OUTER_WIDTH - 16,
        30,
        page=PAGE_SHOW,
        font=TITLE_FONT,
    )

    # Solo on purpose: this is what makes the room one state at a time. Nothing
    # here starts anything else in here, so the solo-frame rule is not broken -
    # a moment starts wheels and chasers, and every one of those lives on
    # another page, in a plain frame.
    room = frame(
        outer,
        vocabulary.display("room_states"),
        LEFT_X,
        68,
        OUTER_WIDTH - 16,
        322,
        page=PAGE_SHOW,
        solo=True,
        # A moment must stop an AUTO that the page-2 duplicate started, which
        # leaves this frame's AUTO button only monitoring it.
        exclude_monitored=False,
        font=TITLE_FONT,
    )
    for function, caption, (x, y, w, h), font in ROOM_STATES:
        master_button(
            room,
            vocabulary.display(function),
            vocabulary.display(caption),
            x,
            y,
            w,
            h,
            font=font,
        )

    hits = frame(
        outer,
        vocabulary.display("hits"),
        LEFT_X,
        330,
        OUTER_WIDTH - 16,
        160,
        page=PAGE_SHOW,
        font=TITLE_FONT,
    )
    # Seven across the row: pitch derived from the frame so adding a hit
    # narrows the buttons instead of pushing the last one off the screen. A hit
    # the show has no function for (the haze, on a rig without a machine) takes
    # no place in the row.
    present = [(f, c) for f, c in HITS if master.get(vocabulary.display(f)) is not None]
    pitch = (OUTER_WIDTH - 16 - 2 * GAP - 4) // max(len(present), 1)
    for index, (function, caption) in enumerate(present):
        master_button(
            hits,
            vocabulary.display(function),
            vocabulary.display(caption),
            GAP + 2 + index * pitch,
            HEADER + 4,
            pitch - 6,
            118,
            font=BIG_FONT,
        )

    panic = frame(
        outer,
        vocabulary.display("panic_frame"),
        LEFT_X,
        500,
        OUTER_WIDTH - 16,
        118,
        page=PAGE_SHOW,
        font=TITLE_FONT,
    )
    # Neither drives a function of its own. StopAll stops every one that is
    # running, which is the only honest answer to "something is on and nobody
    # knows what started it". Blackout answers a different question - it forces
    # the outputs themselves to zero, for when the desk is stuck showing light
    # that no running function accounts for. And unlike StopAll, Blackout is a
    # latch, not a one-shot: qmlui's VCButton::Action::Blackout case toggles
    # `inputOutputMap()->toggleBlackout()` on press (qmlui/virtualconsole/
    # vcbutton.cpp:445-450) - the first APAGON forces the room dark regardless
    # of what AUTO or a moment is still doing underneath, and only a second
    # APAGON lifts it back to that. AUTO restarts nothing while blacked out:
    # it has to follow the second APAGON, not replace it - the help label
    # below says so.
    # The panic pair rides the SMC-PAD's transport buttons - on the device's
    # right edge, physically apart from the pads a hand hammers in the dark.
    stop_all = button(
        panic,
        None,
        vocabulary.display("stop_all_button"),
        GAP + 2,
        HEADER + 4,
        460,
        78,
        action=STOP_ALL,
        key=STOP_ALL_KEY,
        stop_all_fade_ms=STOP_ALL_FADE_MS,
        font=BIG_FONT,
    )
    bind_pad(stop_all, pad_bindings, vocabulary.display("stop_all"))
    blackout = button(
        panic,
        None,
        vocabulary.display("blackout_button"),
        474,
        HEADER + 4,
        200,
        78,
        action=BLACKOUT,
        key=BLACKOUT_KEY,
        font=BIG_FONT,
    )
    bind_pad(blackout, pad_bindings, vocabulary.display("blackout"))
    label(
        panic,
        vocabulary.display("panic_help"),
        680,
        HEADER + 4,
        726,
        78,
        font=HELP_FONT,
    )

    for index, line in enumerate(HELP_LINES):
        label(
            outer,
            vocabulary.display(line if hazes else HELP_WITHOUT_HAZE.get(line, line)),
            LEFT_X,
            HELP_ROW_Y + index * 26,
            RIGHT_X - LEFT_X - GAP,
            24,
            page=PAGE_SHOW,
            font=HELP_FONT,
        )

    # The haze rhythm, on the page the operator is looking at. Solo, because
    # two timers on one pump is twice the haze: pressing a rhythm stops the one
    # that was running, and pressing the running one again stops the haze
    # altogether. The vertical columns are not here and never will be - those
    # only fire while HUMO VERT is held down (`rule_held_column`). No haze
    # machine, no row: an empty solo frame is a promise (`marco vacio`).
    if hazes:
        smoke = frame(
            outer,
            vocabulary.display("haze"),
            LEFT_X,
            SMOKE_ROW_Y,
            RIGHT_X - LEFT_X - GAP,
            SMOKE_ROW_HEIGHT,
            page=PAGE_SHOW,
            solo=True,
            # AUTO starts the one-minute rhythm as a child; choosing another must
            # stop it, or two timers share the pump.
            exclude_monitored=False,
            font=TITLE_FONT,
        )
        pitch = (RIGHT_X - LEFT_X - GAP - 2 * GAP) // len(SMOKE_RHYTHMS)
        for index, (function, caption) in enumerate(SMOKE_RHYTHMS):
            master_button(
                smoke,
                vocabulary.display(function),
                vocabulary.display(caption),
                GAP + index * pitch,
                HEADER + 4,
                pitch - 6,
                SMOKE_BUTTON_HEIGHT,
                font=BIG_FONT,
            )

    # The tempo dial, where the operator is looking, with the hand-built
    # console's tap key. Each layer carries its own multiplier - see
    # `beat_multiplier` - so one tap re-times all of them and none of them
    # loses its proportion to the rest.
    if not tempo_functions and not bpm_tap:
        return
    dial_id = ids.take()
    dial = build_speed_dial(
        outer,
        dial_id,
        vocabulary.display("tempo_dial"),
        RIGHT_X,
        700,
        RIGHT_WIDTH,
        120,
        functions=tempo_functions,
        time_ms=tempo_beat_ms,
        tap_key=TEMPO_TAP_KEY,
        control_bpm=bpm_tap,
    )
    bind_pad(dial, pad_bindings, vocabulary.display("tempo_dial"))
    _on_page(dial, PAGE_SHOW)
    console.widget_ids.append(dial_id)
    # The middle line names the gobo and prism animations only when the show
    # built them: they are what the dial would re-time.
    tempo_lines = (
        "tempo_1",
        tempo_help_line(
            master.get(vocabulary.display("gobo_animation")) is not None,
            master.get(vocabulary.display("prism_animation")) is not None,
            master.get(vocabulary.display("dimmer_chase")) is not None,
        ),
        tempo_close_line(master.get(vocabulary.display("head_movements")) is not None),
    )
    for index, line in enumerate(tempo_lines):
        label(
            outer,
            vocabulary.display(line),
            RIGHT_X,
            824 + index * 20,
            RIGHT_WIDTH,
            20,
            page=PAGE_SHOW,
            font=HELP_FONT,
        )


def _page_control(
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
    master: Mapping[str, int],
    mover_fixture_ids,
    movement_functions,
    tempo_beat_ms,
    palette: Mapping[str, tuple[int, int, int]],
    pad_bindings: Mapping[str, int],
    vocabulary: Names,
    short_colour: Mapping[str, str],
    mix_code: Mapping[str, str],
    has_smoke_machine: bool,
) -> None:
    """Page 3: direct controls that remain useful beside the play families."""
    # Page 3's one haze control is the vertical column's light, and its beam
    # wheel frame is built only from beam colour scenes; without either the
    # page title does not promise it. The column's light is built from the
    # panels alone, so haze is promised only where a smoke machine is patched
    # too (2026-09-25: "y humo" on a rig with panels and no smoke machine).
    has_haze_light = (
        has_smoke_machine and master.get(vocabulary.display("vertical_smoke")) is not None
    )
    label(
        outer,
        vocabulary.display(
            page_control_title(
                has_haze_light, bool(beam_colors.scene_ids), has_heads=bool(mover_fixture_ids)
            )
        ),
        LEFT_X,
        30,
        OUTER_WIDTH - 16,
        30,
        page=PAGE_CONTROL,
        font=TITLE_FONT,
    )

    # The banks are one frame per fixture group, and the number of groups is
    # not a constant: a fifth group (the two MAC WASH, 2026-08-31) pushed this
    # column and everything under it off the bottom of the screen, which the
    # `consola` rule reported and the generator's own "fits on one screen" line
    # had cheerfully denied. So the pitch comes from the room left between the
    # layers above and the dimmer frame below, never from a number typed here.
    # Held, with ForceLTP, since 2026-09-02: RGB mixes HTP, so a latched bank
    # on top of a running state never showed its colour - AUTO on cyan plus
    # key 1 was white on twenty-seven fixtures (cross-audit). A Flash with
    # Override and ForceLTP writes past the HTP compare and the state's own
    # wheel steps, so "the heads are red" is true for as long as the key is
    # down, and the state's colour comes straight back on release. A plain
    # frame: momentary buttons have nothing for a solo frame to stop.
    y = BANK_COLUMN_TOP
    bank_pitch = bank_pitch_for(len(banks))
    for bank in banks:
        element = frame(
            outer,
            vocabulary.render("bank_frame", group=bank.group_name),
            LEFT_X,
            y,
            LEFT_WIDTH,
            bank_pitch - 6,
            page=PAGE_CONTROL,
            font=TITLE_FONT,
        )
        # Keys 1-0 follow the bank's key list - eight solids, then the old
        # blue/red splits on 9 and 0 (restored 2026-08-28). The solids the
        # splits displaced stay in the row, keyless, after them.
        keyed = bank.key_ids[: len(BANK_KEYS)] or bank.scene_ids[: len(BANK_KEYS)]
        keyless = [fid for fid in bank.scene_ids if fid not in keyed]
        pitch = (LEFT_WIDTH - 2 * GAP) // max(len(keyed) + len(keyless), 1)
        for index, function_id in enumerate(keyed + keyless):
            name = names.get(function_id, "")
            split = " / " in name
            button(
                element,
                function_id,
                _mix_caption(name, mix_code) if split else _bank_caption(name, short_colour),
                x=GAP + index * pitch,
                y=HEADER,
                w=pitch - 3,
                h=44,
                key=BANK_KEYS[index] if index < len(keyed) else None,
                action=FLASH,
                flash_override=True,
                flash_force_ltp=True,
                background=_swatch(name, palette),
                foreground=_swatch(name, palette, second=True) if split else DEFAULT,
                font=TINY_FONT if split else SMALL_FONT,
            )
        y += bank_pitch

    # A rig with no fader dimmer and no fixture strobe has nothing for this
    # frame to hold (2026-09-26, round G), so it is not drawn empty.
    if any(master.get(vocabulary.display(f)) is not None for f, _ in DIMMER_CHASES):
        dimmers = frame(
            outer,
            vocabulary.display("intensity_chases"),
            LEFT_X,
            y,
            LEFT_WIDTH,
            DIMMER_FRAME_HEIGHT,
            page=PAGE_CONTROL,
            font=TITLE_FONT,
        )
        for index, (function_id, caption_id) in enumerate(DIMMER_CHASES):
            column, row = index % 3, index // 3
            master_button(
                dimmers,
                vocabulary.display(function_id),
                vocabulary.display(caption_id),
                GAP + column * 170,
                HEADER + row * 52,
                166,
                46,
            )

    # Below the audio triggers (they end at y=440): the left column is full,
    # four colour banks deep.
    grand_master_y = 450
    # The bass bar's target has to be a widget (SpectrumBar presses widgets,
    # not functions), so its plain white hit gets a button of its own here,
    # beside the audio triggers that press it.
    master_button(
        outer,
        vocabulary.display("bass_hit"),
        vocabulary.display("bass_button"),
        RIGHT_X + GRAND_MASTER_WIDTH + GAP,
        grand_master_y,
        RIGHT_WIDTH - GRAND_MASTER_WIDTH - GAP,
        60,
        page=PAGE_CONTROL,
    )
    grand_master_id = ids.take()
    grand_master = build_grand_master_slider(
        outer,
        grand_master_id,
        vocabulary.display("grand_master"),
        RIGHT_X,
        grand_master_y,
        GRAND_MASTER_WIDTH,
        GRAND_MASTER_HEIGHT,
    )
    bind_pad(grand_master, pad_bindings, vocabulary.display("grand_master"))
    _on_page(grand_master, PAGE_CONTROL)
    console.widget_ids.append(grand_master_id)
    for index, line in enumerate(GRAND_MASTER_LINES):
        label(
            outer,
            vocabulary.display(line),
            RIGHT_X,
            grand_master_y + GRAND_MASTER_HEIGHT + GAP + index * 22,
            RIGHT_WIDTH,
            20,
            page=PAGE_CONTROL,
            font=HELP_FONT,
        )

    # The vertical smoke's light: latched on purpose - the column lasts as
    # long as it lasts, and somebody presses it off when it is over.
    # Its help explains that button, so it goes where the button goes.
    if has_haze_light:
        master_button(
            outer,
            vocabulary.display("vertical_smoke"),
            vocabulary.display("vertical_smoke_light"),
            RIGHT_X,
            716,
            RIGHT_WIDTH,
            60,
            page=PAGE_CONTROL,
        )
        label(
            outer,
            vocabulary.display("vertical_smoke_help"),
            RIGHT_X,
            782,
            RIGHT_WIDTH,
            60,
            page=PAGE_CONTROL,
            font=HELP_FONT,
        )

    # The beams' own colour wheel remains held here. A latched colour-wheel
    # pick on JUGAR would stop the rig wheel and leave every RGB fixture dark.
    _wheel_frame(
        outer,
        button,
        frame,
        names,
        vocabulary,
        beam_colors.scene_ids,
        vocabulary.display("beam_wheel_frame"),
        "Color Beam - ",
        MIDDLE_X,
        68,
        MIDDLE_WIDTH,
        150,
        PAGE_CONTROL,
        columns=12,
    )

    # Keep the aiming controls directly below the beam wheel. The outer frame
    # is 892px tall, so the pad leaves the same 6px inset at its bottom after
    # taking the space released by moving the wheel up (2026-09-03). A rig
    # with nothing that pans and tilts gets no pad to aim nothing with.
    if mover_fixture_ids:
        label(
            outer,
            vocabulary.display("aim_frame"),
            MIDDLE_X,
            224,
            MIDDLE_WIDTH,
            20,
            page=PAGE_CONTROL,
            font=HELP_FONT,
        )
        pad_id = ids.take()
        pad = build_xy_pad(
            outer,
            pad_id,
            vocabulary.display("xy_pad"),
            MIDDLE_X,
            250,
            MIDDLE_WIDTH,
            636,
            fixture_ids=list(mover_fixture_ids),
        )
        _on_page(pad, PAGE_CONTROL)
        console.widget_ids.append(pad_id)

    # The movement dial stays with the direct controls and on the same tap key
    # as page 1's tempo. It re-times each rotation AND the EFX
    # under it, chaser fade included, so the figure stays the same fraction
    # of its step whatever the room is doing.
    if movement_functions:
        dial_id = ids.take()
        dial = build_speed_dial(
            outer,
            dial_id,
            vocabulary.display("movement_speed"),
            RIGHT_X,
            68,
            124,
            150,
            functions=movement_functions,
            time_ms=tempo_beat_ms,
            tap_key=TEMPO_TAP_KEY,
        )
        bind_pad(dial, pad_bindings, vocabulary.display("movement_speed"))
        _on_page(dial, PAGE_CONTROL)
        console.widget_ids.append(dial_id)
        for index, line in enumerate(MOVEMENT_DIAL_LINES):
            label(
                outer,
                vocabulary.display(line),
                RIGHT_X,
                228 + index * 22,
                RIGHT_WIDTH,
                20,
                page=PAGE_CONTROL,
                font=HELP_FONT,
            )


def _page_library(
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
    palette: Mapping[str, tuple[int, int, int]],
    vocabulary: Names,
    mix_code: Mapping[str, str],
    has_bars: bool,
    has_panels: bool,
) -> None:
    """Page 4: the material the show is built from, not buttons for a set."""
    label(
        outer,
        vocabulary.display("page_library"),
        LEFT_X,
        30,
        OUTER_WIDTH - 16,
        30,
        page=PAGE_LIBRARY,
        font=TITLE_FONT,
    )

    # Held with ForceLTP like the banks (2026-09-02): a two-colour scene on a
    # Toggle adds to the running state's colour instead of showing its own.
    # The blue/red pair lives on the bank's keys 9/0 (restored 2026-08-28); a
    # second button here would always look off. A rig whose banks hold no
    # other mix (one beam, 2026-09-26) gets no frame: it would be empty.
    library_splits = [[fid for fid in bank.split_ids if fid not in bank.key_ids] for bank in banks]
    if any(library_splits):
        mixes = frame(
            outer,
            vocabulary.display("mixes_frame"),
            LEFT_X,
            68,
            LEFT_WIDTH,
            230,
            page=PAGE_LIBRARY,
            pages=len(banks) or 1,
            font=TITLE_FONT,
        )
        for page, bank in enumerate(banks):
            label(
                mixes,
                vocabulary.render("group_label", group=bank.group_name),
                GAP,
                HEADER,
                512,
                20,
                page=page,
                font=HELP_FONT,
            )
            for index, function_id in enumerate(library_splits[page]):
                column, row = index % 10, index // 10
                name = names.get(function_id, "")
                _on_page(
                    button(
                        mixes,
                        function_id,
                        _mix_caption(name, mix_code),
                        x=GAP + column * 51,
                        y=HEADER + 24 + row * 51,
                        w=48,
                        h=45,
                        action=FLASH,
                        flash_override=True,
                        flash_force_ltp=True,
                        background=_swatch(name, palette),
                        foreground=_swatch(name, palette, second=True),
                        font=TINY_FONT,
                    ),
                    page,
                )

    _wheel_frame(
        outer,
        button,
        frame,
        names,
        vocabulary,
        beam_subsets.multicolor_scene_ids if beam_subsets is not None else [],
        vocabulary.display("multicolour_frame"),
        "MultiColor - ",
        LEFT_X,
        306,
        LEFT_WIDTH,
        92,
        PAGE_LIBRARY,
        columns=8,
    )

    # No matrix to press (a rig of two panels, 2026-09-26): no frame, and no
    # caption promising patterns on them.
    if any(generated.matrix_ids for generated in matrices):
        matrix_frame = frame(
            outer,
            vocabulary.display(matrices_frame_caption(has_bars, has_panels)),
            MIDDLE_X,
            68,
            MIDDLE_WIDTH,
            300,
            page=PAGE_LIBRARY,
            solo=True,
            pages=len(matrices) or 1,
            font=TITLE_FONT,
        )
        for page, generated in enumerate(matrices):
            group = _before(names.get(_first(generated.matrix_ids), ""), " - ")
            label(
                matrix_frame,
                vocabulary.render("group_label", group=group),
                GAP,
                HEADER,
                400,
                20,
                page=page,
                font=HELP_FONT,
            )
            step = (MIDDLE_WIDTH - GAP * 2) // MATRIX_COLUMNS
            for index, function_id in enumerate(generated.matrix_ids):
                column, row = index % MATRIX_COLUMNS, index // MATRIX_COLUMNS
                _on_page(
                    button(
                        matrix_frame,
                        function_id,
                        _after(names.get(function_id, ""), " - "),
                        x=GAP + column * step,
                        y=HEADER + 24 + row * MATRIX_ROW_HEIGHT,
                        w=step - 6,
                        h=MATRIX_BUTTON_HEIGHT,
                        font=SMALL_FONT,
                    ),
                    page,
                )

    # Each group's own colour wheel and its matrix cycle. Both start the looks
    # sitting in the solo frames above, so both live in a plain frame.
    cycles = frame(
        outer,
        vocabulary.display("group_wheels_frame"),
        MIDDLE_X,
        376,
        MIDDLE_WIDTH,
        190,
        page=PAGE_LIBRARY,
        font=TITLE_FONT,
    )
    # The wheel captions are rendered from the bank, not parsed from the
    # wheel's name (ruling B8).
    entries = [
        (b.wheel_id, vocabulary.render("group_colour_wheel_caption", group=b.group_name))
        for b in banks
        if b.wheel_id is not None
    ]
    entries += [
        (b.mix_wheel_id, vocabulary.render("group_mix_wheel_caption", group=b.group_name))
        for b in banks
        if b.mix_wheel_id is not None
    ]
    cycle_marker = template_affixes(vocabulary, "cycle")[0]
    entries += [
        (m.chaser_id, _after(names.get(m.chaser_id, ""), cycle_marker))
        for m in matrices
        if m.chaser_id is not None
    ]
    # The panels' own cycle belongs here and not among the effects it starts:
    # a chaser sharing a solo frame with its own steps dies as it begins.
    if builtins.chaser_id is not None:
        entries.append(
            (
                builtins.chaser_id,
                _after(names.get(builtins.chaser_id, ""), cycle_marker),
            )
        )
    for index, (function_id, caption) in enumerate(entries):
        column, row = index % 5, index // 5
        button(
            cycles,
            function_id,
            caption,
            x=GAP + column * 122,
            y=HEADER + row * 50,
            w=116,
            h=44,
            font=SMALL_FONT,
        )

    if builtins.scene_ids:
        panels = frame(
            outer,
            vocabulary.render(panels_frame_caption(has_panels), count=len(builtins.scene_ids)),
            MIDDLE_X,
            580,
            MIDDLE_WIDTH,
            244,
            page=PAGE_LIBRARY,
            solo=True,
            font=TITLE_FONT,
        )
        for index, function_id in enumerate(builtins.scene_ids):
            column, row = index % 12, index // 12
            button(
                panels,
                function_id,
                _after(names.get(function_id, ""), " - "),
                x=GAP + column * 51,
                y=HEADER + row * 52,
                w=47,
                h=46,
                font=TINY_FONT,
            )

    if builtins.speed_channels:
        # The live fader over the panels' speed channel, beside the effects it
        # paces - the hand-built console's "Strobo LED Effect Speed", whose
        # slider sat at 253 with the show's own sequence stepping 160-255.
        # The channel is in the Speed group, so it is LTP, not HTP: the slider
        # monitors the running value until somebody moves it, and from then
        # on its Override fader wins outright - at zero too, which is the
        # slowest, not "the cycle's" - until the red reset X hands the channel
        # back (`VCSlider::writeDMXLevel`; cross-audit, 2026-09-02).
        slider_id = ids.take()
        slider = build_level_slider(
            outer,
            slider_id,
            vocabulary.display("panel_speed"),
            RIGHT_X,
            580,
            90,
            244,
            channels=list(builtins.speed_channels),
        )
        _on_page(slider, PAGE_LIBRARY)
        console.widget_ids.append(slider_id)
        label(
            outer,
            vocabulary.display("panel_speed_help"),
            RIGHT_X + 96,
            580,
            RIGHT_WIDTH - 96,
            120,
            page=PAGE_LIBRARY,
            font=HELP_FONT,
        )
        # The old "Strobo LED - Speed Auto", beside the fader it shares the
        # channel with: the pace rides 160-255 on its own until somebody
        # stops it (HTP - the raised fader wins while it is higher).
        master_button(
            outer,
            vocabulary.display("panel_speed_auto"),
            vocabulary.display("panel_speed_auto_button"),
            RIGHT_X + 96,
            704,
            RIGHT_WIDTH - 96,
            60,
            page=PAGE_LIBRARY,
            font=SMALL_FONT,
        )

    if matrices and matrices[0].matrix_ids:
        matrix_widget_id = ids.take()
        control = build_matrix_control(
            outer,
            matrix_widget_id,
            vocabulary.display("live_matrix"),
            RIGHT_X,
            68,
            RIGHT_WIDTH,
            200,
            function_id=matrices[0].matrix_ids[0],
            algorithms=list(matrix_algorithms),
        )
        _on_page(control, PAGE_LIBRARY)
        console.widget_ids.append(matrix_widget_id)

    lines = library_help_lines(
        bool(builtins.scene_ids),
        has_panels,
        has_mixes=any(library_splits),
        has_matrices=any(generated.matrix_ids for generated in matrices),
    )
    for index, line in enumerate(lines):
        label(
            outer,
            LIBRARY_SEPARATOR
            if line is None
            else vocabulary.render(line, count=len(builtins.scene_ids)),
            LEFT_X,
            410 + index * 26,
            LEFT_WIDTH,
            24,
            page=PAGE_LIBRARY,
            font=HELP_FONT,
        )


def _wheel_frame(
    outer,
    button,
    frame,
    names,
    vocabulary: Names,
    scene_ids,
    caption,
    marker,
    x,
    y,
    width,
    height,
    page,
    columns,
) -> None:
    """A frame of held wheel positions - gobos, beam colours, prism.

    Held (Flash with Override priority), not latched, since 2026-09-02: a
    Toggle pick on an LTP wheel lasted exactly until the running state's own
    chaser stepped - Gobo Animacion every 4 s, the prism dance every 8 s, the
    colour wheel every 3.3 s - because the step's new fader is appended after
    the button's and wins (cross-audit). An Override fader is placed last
    whatever starts after it, so the pick holds while the finger does, and the
    state writes the wheel back the moment it lifts.
    """
    if not scene_ids:
        return
    element = frame(
        outer,
        vocabulary.render("hold_frame", caption=caption),
        x,
        y,
        width,
        height,
        page=page,
        font=TITLE_FONT,
    )
    step = (width - GAP * 2) // columns
    for index, function_id in enumerate(scene_ids):
        column, row = index % columns, index // columns
        caption = _after(names.get(function_id, ""), marker)
        long_name = LONG_WHEEL_NAME.get(caption)
        button(
            element,
            function_id,
            caption if long_name is None else vocabulary.display(long_name),
            x=GAP + column * step,
            y=HEADER + row * 52,
            w=step - 4,
            h=46,
            action=FLASH,
            flash_override=True,
            font=TINY_FONT,
        )


def _root_frame(root: etree._Element) -> etree._Element:
    console = find_local(root, "VirtualConsole")
    if console is None:
        raise ValueError("workspace has no <VirtualConsole>")
    frame = find_local(console, "Frame")
    if frame is None:
        raise ValueError("Virtual Console has no root <Frame>")
    return frame


def _function_names(workspace: Workspace) -> dict[int, str]:
    return {
        int(f.attrib["ID"]): f.attrib.get("Name", "")
        for f in workspace.engine
        if localname(f) == "Function" and f.attrib.get("ID")
    }


def _on_page(widget: etree._Element, page: int | None) -> None:
    """Which page of a multipage frame this widget belongs to; 0 is implicit."""
    if page:
        widget.set("Page", str(page))


def _first(ids):
    return ids[0] if ids else None


def _swatch(name: str, palette: Mapping[str, tuple[int, int, int]], second: bool = False) -> str:
    """The ARGB of the palette colour a scene is named after, or Default."""
    parts = [p.strip() for p in name.split(" / ")]
    text = parts[1] if second and len(parts) > 1 else parts[0]
    for color_name in sorted(palette, key=len, reverse=True):
        if text == color_name or text.startswith(f"{color_name} "):
            return str(argb_from_rgb(palette[color_name]))
    return DEFAULT


def _bank_caption(name: str, short_colour: Mapping[str, str]) -> str:
    """ "Rojo BarrasLed" is a red button in the bars' bank: it says "Rojo"."""
    first = name.split(" ", maxsplit=1)[0] if name else ""
    return short_colour.get(first, first)


def _mix_caption(name: str, mix_code: Mapping[str, str]) -> str:
    """ "Rojo / Azul PAR" reads as "Ro/Az" on a 44px button.

    Two letters, not one: Azul and Amarillo both start with an A, so a
    one-letter code gave six pairs of buttons the same label.
    """
    parts = [p.strip() for p in name.split(" / ")]
    if len(parts) < 2:
        return ""
    first = parts[0].split(" ")[0]
    second = parts[1].split(" ")[0]
    return f"{mix_code.get(first, first[:2])}/{mix_code.get(second, second[:2])}"


def _after(name: str, marker: str) -> str:
    _, separator, tail = name.partition(marker)
    return tail if separator else name


def _before(name: str, marker: str) -> str:
    head, separator, _ = name.partition(marker)
    return head if separator else name


def _set_canvas(root: etree._Element, canvas: tuple[int, int]) -> None:
    console = find_local(root, "VirtualConsole")
    properties = find_local(console, "Properties")
    if properties is None:
        return
    size = find_local(properties, "Size")
    if size is None:
        return
    size.set("Width", str(canvas[0]))
    size.set("Height", str(canvas[1]))
