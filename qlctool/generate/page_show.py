"""Page 1 of the live console: the state the room is in, the hits, and the panic button.

Moved verbatim out of `live_console` (2026-09-27 split). The widget closures
(`button`, `master_button`, `frame`, `label`) and the id counter are the
console's own, so the widget ids come out in the order they always did.
"""

from collections.abc import Callable, Mapping, Sequence

from lxml import etree

from ..names.names import Names
from ..vc.button import BLACKOUT, STOP_ALL
from ..vc.dial_function import DialFunction
from ..vc.speed_dial import build_speed_dial
from .bind_pad import bind_pad
from .console_ids import ConsoleIds
from .console_layout import (
    BIG_FONT,
    BLACKOUT_KEY,
    GAP,
    HEADER,
    HELP_FONT,
    HELP_LINES,
    HELP_ROW_Y,
    HELP_WITHOUT_HAZE,
    HITS,
    LEFT_X,
    OUTER_WIDTH,
    PAGE_SHOW,
    RIGHT_WIDTH,
    RIGHT_X,
    ROOM_STATES,
    SMOKE_BUTTON_HEIGHT,
    SMOKE_RHYTHMS,
    SMOKE_ROW_HEIGHT,
    SMOKE_ROW_Y,
    STOP_ALL_FADE_MS,
    STOP_ALL_KEY,
    TEMPO_TAP_KEY,
    TITLE_FONT,
)
from .generated_console import GeneratedConsole
from .on_page import on_page
from .tempo_close_line import tempo_close_line
from .tempo_help_line import tempo_help_line


def page_show(
    outer: etree._Element,
    button: Callable[..., etree._Element],
    master_button: Callable[..., etree._Element | None],
    frame: Callable[..., etree._Element],
    label: Callable[..., etree._Element],
    ids: ConsoleIds,
    console: GeneratedConsole,
    master: Mapping[str, int],
    tempo_functions: Sequence[DialFunction],
    bpm_tap: bool,
    tempo_beat_ms: int,
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
    on_page(dial, PAGE_SHOW)
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
