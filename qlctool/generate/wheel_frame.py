"""A frame of held wheel positions on the live console: gobos, beam colours, prism.

Moved verbatim out of `live_console` (2026-09-27 split). `button` and `frame`
are the console's own widget closures, which hand out the widget ids in order.
"""

from collections.abc import Callable, Mapping, Sequence

from lxml import etree

from ..names.names import Names
from ..vc.build_button import FLASH
from .after_marker import after_marker
from .console_layout import GAP, HEADER, LONG_WHEEL_NAME, TINY_FONT, TITLE_FONT


def wheel_frame(
    outer: etree._Element,
    button: Callable[..., etree._Element],
    frame: Callable[..., etree._Element],
    names: Mapping[int, str],
    vocabulary: Names,
    scene_ids: Sequence[int],
    caption: str,
    marker: str,
    x: int,
    y: int,
    width: int,
    height: int,
    page: int,
    columns: int,
) -> None:
    """A frame of held wheel positions - gobos, beam colours, prism.

    Held (Flash with Override priority), not latched, since 2026-09-02: a
    Toggle pick on an LTP wheel lasted exactly until the running state's own
    chaser stepped - Gobo Animacion every 4 s, the prism dance every 8 s, the
    colour wheel every 3.3 s - because the step's new fader is appended after
    the button's and wins (cross-audit). An Override fader is placed last
    whatever starts after it, so the pick holds while the finger does, and the
    state writes the wheel back the moment it lifts.
    """
    if not scene_ids:
        return
    element = frame(
        outer,
        vocabulary.render("hold_frame", caption=caption),
        x,
        y,
        width,
        height,
        page=page,
        font=TITLE_FONT,
    )
    step = (width - GAP * 2) // columns
    for index, function_id in enumerate(scene_ids):
        column, row = index % columns, index // columns
        caption = after_marker(names.get(function_id, ""), marker)
        long_name = LONG_WHEEL_NAME.get(caption)
        button(
            element,
            function_id,
            caption if long_name is None else vocabulary.display(long_name),
            x=GAP + column * step,
            y=HEADER + row * 52,
            w=step - 4,
            h=46,
            action=FLASH,
            flash_override=True,
            font=TINY_FONT,
        )
