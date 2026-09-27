"""Page 1's hits frame: they add to whatever state is running, not replace it.

Moved verbatim out of `page_show` (2026-09-27 split). `master_button` and
`frame` are the console's own widget closures, so the widget ids come out in
the order they always did.
"""

from collections.abc import Callable, Mapping

from lxml import etree

from ..names.names import Names
from .console_layout import BIG_FONT, GAP, HEADER, HITS, LEFT_X, OUTER_WIDTH, PAGE_SHOW, TITLE_FONT


def hits(
    outer: etree._Element,
    master_button: Callable[..., etree._Element | None],
    frame: Callable[..., etree._Element],
    master: Mapping[str, int],
    vocabulary: Names,
) -> None:
    """The hits: they add to whatever state is running instead of replacing it."""
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
