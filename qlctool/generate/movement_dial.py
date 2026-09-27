"""Page 3's movement dial: re-times the heads' rotation and the EFX under it.

Moved verbatim out of `page_control` (2026-09-27 split). `label` is the
console's own widget closure, and `ids` its id counter, so the widget ids
come out in the order they always did.
"""

from collections.abc import Callable, Mapping, Sequence

from lxml import etree

from ..names.names import Names
from ..vc.build_speed_dial import build_speed_dial
from ..vc.dial_function import DialFunction
from .bind_pad import bind_pad
from .console_ids import ConsoleIds
from .console_layout import (
    HELP_FONT,
    MOVEMENT_DIAL_LINES,
    PAGE_CONTROL,
    RIGHT_WIDTH,
    RIGHT_X,
    TEMPO_TAP_KEY,
)
from .generated_console import GeneratedConsole
from .on_page import on_page


def movement_dial(
    outer: etree._Element,
    label: Callable[..., etree._Element],
    ids: ConsoleIds,
    console: GeneratedConsole,
    movement_functions: Sequence[DialFunction],
    tempo_beat_ms: int,
    pad_bindings: Mapping[str, int],
    vocabulary: Names,
) -> None:
    """The movement dial stays with the direct controls and on the same tap key
    as page 1's tempo. It re-times each rotation AND the EFX under it, chaser
    fade included, so the figure stays the same fraction of its step whatever
    the room is doing.
    """
    if not movement_functions:
        return
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
    on_page(dial, PAGE_CONTROL)
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
