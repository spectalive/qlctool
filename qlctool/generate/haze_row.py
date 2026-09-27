"""Page 1's haze row: how often the haze fires on its own, one rhythm at a time.

Moved verbatim out of `page_show` (2026-09-27 split). `master_button` and
`frame` are the console's own widget closures, so the widget ids come out in
the order they always did.
"""

from collections.abc import Callable

from lxml import etree

from ..names.names import Names
from .console_layout import (
    BIG_FONT,
    GAP,
    HEADER,
    LEFT_X,
    PAGE_SHOW,
    RIGHT_X,
    SMOKE_BUTTON_HEIGHT,
    SMOKE_RHYTHMS,
    SMOKE_ROW_HEIGHT,
    SMOKE_ROW_Y,
    TITLE_FONT,
)


def haze_row(
    outer: etree._Element,
    master_button: Callable[..., etree._Element | None],
    frame: Callable[..., etree._Element],
    hazes: bool,
    vocabulary: Names,
) -> None:
    """The haze rhythm, on the page the operator is looking at. Solo, because
    two timers on one pump is twice the haze: pressing a rhythm stops the one
    that was running, and pressing the running one again stops the haze
    altogether. The vertical columns are not here and never will be - those
    only fire while HUMO VERT is held down (`rule_held_column`). No haze
    machine, no row: an empty solo frame is a promise (`marco vacio`).
    """
    if not hazes:
        return
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
