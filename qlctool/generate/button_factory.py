"""Factory for the live console's `button` closure: one button widget, its own id.

Moved verbatim out of `generate_live_console` (2026-09-27 split): the closure
itself is unchanged, only built by a factory that takes the state it closes
over as explicit arguments.
"""

from collections.abc import Callable
from typing import Any

from lxml import etree

from ..vc.button import build_button
from .console_ids import ConsoleIds
from .generated_console import GeneratedConsole
from .on_page import on_page


def button_factory(
    ids: ConsoleIds,
    console: GeneratedConsole,
    widget_of: dict[int, int],
) -> Callable[..., etree._Element]:
    """Build the console's `button` closure, bound to its widget id counter."""

    def button(
        parent: etree._Element,
        function_id: int | None,
        caption: str,
        x: int,
        y: int,
        w: int,
        h: int,
        page: int | None = None,
        **kwargs: Any,
    ) -> etree._Element:
        widget_id = ids.take()
        element = build_button(
            parent,
            widget_id,
            caption,
            function_id,
            x=x,
            y=y,
            width=w,
            height=h,
            **kwargs,
        )
        on_page(element, page)
        console.button_ids.append(widget_id)
        console.widget_ids.append(widget_id)
        if function_id is not None:
            widget_of[function_id] = widget_id
        return element

    return button
