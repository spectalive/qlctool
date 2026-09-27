"""The live console's outer, multipage frame: everything else sits inside it.

Moved verbatim out of `generate_live_console` (2026-09-27 split). `frame` is
the console's own widget closure, so the widget ids come out in the order
they always did.
"""

from collections.abc import Callable, Mapping

from lxml import etree

from ..names.names import Names
from .bind_pad import bind_pad
from .console_layout import (
    OUTER_HEIGHT,
    OUTER_WIDTH,
    OUTER_X,
    OUTER_Y,
    PAGE_NEXT_KEY,
    PAGE_PREVIOUS_KEY,
    PAGES,
    TITLE_FONT,
)


def console_outer_frame(
    console_root: etree._Element,
    frame: Callable[..., etree._Element],
    pad_bindings: Mapping[str, int],
    vocabulary: Names,
) -> etree._Element:
    """When a pad profile is given, its arrow buttons page the console: a
    frame's Next Page is external control 0 and Previous Page is 1 (qmlui
    vcframe.h). Without a pad, nothing is bound.
    """
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
    bind_pad(outer, pad_bindings, vocabulary.display("page_next"))
    bind_pad(outer, pad_bindings, vocabulary.display("page_previous"), source_id=1)
    return outer
