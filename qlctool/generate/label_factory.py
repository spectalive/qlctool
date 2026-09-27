"""Factory for the live console's `label` closure: one label widget, its own id.

Moved verbatim out of `generate_live_console` (2026-09-27 split): the closure
itself is unchanged, only built by a factory that takes the state it closes
over as explicit arguments.
"""

from collections.abc import Callable

from lxml import etree

from ..vc.appearance import DEFAULT
from ..vc.label import build_label
from .console_ids import ConsoleIds
from .generated_console import GeneratedConsole
from .on_page import on_page


def label_factory(
    ids: ConsoleIds,
    console: GeneratedConsole,
) -> Callable[..., etree._Element]:
    """Build the console's `label` closure, bound to its widget id counter."""

    def label(
        parent: etree._Element,
        caption: str,
        x: int,
        y: int,
        w: int,
        h: int,
        page: int | None = None,
        font: str = DEFAULT,
    ) -> etree._Element:
        widget_id = ids.take()
        element = build_label(parent, widget_id, caption, x, y, w, h, font=font)
        on_page(element, page)
        console.widget_ids.append(widget_id)
        return element

    return label
