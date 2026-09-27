"""Page 1's room-state frame: the room is in exactly one state at a time.

Moved verbatim out of `page_show` (2026-09-27 split). `master_button` and
`frame` are the console's own widget closures, so the widget ids come out in
the order they always did.
"""

from collections.abc import Callable

from lxml import etree

from ..names.names import Names
from .console_layout import LEFT_X, OUTER_WIDTH, PAGE_SHOW, ROOM_STATES, TITLE_FONT


def room_states(
    outer: etree._Element,
    master_button: Callable[..., etree._Element | None],
    frame: Callable[..., etree._Element],
    vocabulary: Names,
) -> None:
    """The room's state: one at a time, biggest first."""
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
