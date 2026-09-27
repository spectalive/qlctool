"""Page 1 of the live console: the state the room is in, the hits, and the panic button.

Moved verbatim out of `live_console` (2026-09-27 split). The widget closures
(`button`, `master_button`, `frame`, `label`) and the id counter are the
console's own, so the widget ids come out in the order they always did.
"""

from collections.abc import Callable, Mapping, Sequence

from lxml import etree

from ..names.names import Names
from ..vc.dial_function import DialFunction
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
    RIGHT_X,
    SMOKE_RHYTHMS,
    TITLE_FONT,
)
from .generated_console import GeneratedConsole
from .haze_row import haze_row
from .hits import hits
from .panic import panic
from .room_states import room_states
from .tempo_dial import tempo_dial


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

    tempo_dial(
        outer,
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
