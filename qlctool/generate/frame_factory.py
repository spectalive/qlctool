"""Factory for the live console's `frame` closure: one frame widget, its own id.

Moved verbatim out of `generate_live_console` (2026-09-27 split): the closure
itself is unchanged, only built by a factory that takes the state it closes
over as explicit arguments.
"""

from collections.abc import Callable
from typing import Any

from lxml import etree

from ..vc.frame import build_frame
from .console_ids import ConsoleIds
from .generated_console import GeneratedConsole
from .on_page import on_page


def frame_factory(
    ids: ConsoleIds,
    console: GeneratedConsole,
) -> Callable[..., etree._Element]:
    """Build the console's `frame` closure, bound to its widget id counter."""

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

    return frame
