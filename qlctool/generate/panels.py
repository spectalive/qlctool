"""Page 4's built-in effects frame: the panels' own forty-two programmes, one solo frame.

Moved verbatim out of `page_library` (2026-09-27 split). `button` and `frame`
are the console's own widget closures, so the widget ids come out in the
order they always did.
"""

from collections.abc import Callable, Mapping

from lxml import etree

from ..names.names import Names
from .after_marker import after_marker
from .console_layout import (
    GAP,
    HEADER,
    MIDDLE_WIDTH,
    MIDDLE_X,
    PAGE_LIBRARY,
    TINY_FONT,
    TITLE_FONT,
)
from .generated_builtins import GeneratedBuiltins
from .panels_frame_caption import panels_frame_caption


def panels(
    outer: etree._Element,
    button: Callable[..., etree._Element],
    frame: Callable[..., etree._Element],
    names: Mapping[int, str],
    builtins: GeneratedBuiltins,
    has_panels: bool,
    vocabulary: Names,
) -> None:
    """A rig with no built-in effects gets no frame promising them."""
    if not builtins.scene_ids:
        return
    panels = frame(
        outer,
        vocabulary.render(panels_frame_caption(has_panels), count=len(builtins.scene_ids)),
        MIDDLE_X,
        580,
        MIDDLE_WIDTH,
        244,
        page=PAGE_LIBRARY,
        solo=True,
        font=TITLE_FONT,
    )
    for index, function_id in enumerate(builtins.scene_ids):
        column, row = index % 12, index // 12
        button(
            panels,
            function_id,
            after_marker(names.get(function_id, ""), " - "),
            x=GAP + column * 51,
            y=HEADER + row * 52,
            w=47,
            h=46,
            font=TINY_FONT,
        )
