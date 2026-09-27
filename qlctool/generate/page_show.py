"""Page 1 of the live console: the state the room is in, the hits, and the panic button.

Moved verbatim out of `live_console` (2026-09-27 split). The widget closures
(`button`, `master_button`, `frame`, `label`) and the id counter are the
console's own, so the widget ids come out in the order they always did.
"""

from collections.abc import Callable, Mapping, Sequence

from lxml import etree

from ..names.names import Names
from ..vc.dial_function import DialFunction
from ..vc.speed_dial import build_speed_dial
from .bind_pad import bind_pad
from .console_ids import ConsoleIds
from .console_layout import (
    GAP,
    HELP_FONT,
    HELP_LINES,
    HELP_ROW_Y,
    HELP_WITHOUT_HAZE,
    LEFT_X,
    OUTER_WIDTH,
    PAGE_SHOW,
    RIGHT_WIDTH,
    RIGHT_X,
    SMOKE_RHYTHMS,
    TEMPO_TAP_KEY,
    TITLE_FONT,
)
from .generated_console import GeneratedConsole
from .haze_row import haze_row
from .hits import hits
from .on_page import on_page
from .panic import panic
from .room_states import room_states
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

    room_states(outer, master_button, frame, vocabulary)

    hits(outer, master_button, frame, master, vocabulary)

    panic(outer, button, frame, label, pad_bindings, vocabulary)

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

    haze_row(outer, master_button, frame, hazes, vocabulary)

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
