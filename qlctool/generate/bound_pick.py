"""One manual pick bound as a master button, so a moment can hold it (e.g. rainbows)."""

from collections.abc import Callable

from lxml import etree

from ..names.names import Names
from .grid_position import grid_position
from .pick_caption import pick_caption
from .play_page_layout import SMALL_BUTTON_HEIGHT


def bound_pick(
    master_button: Callable[..., object],
    parent: etree._Element,
    name: str,
    function_id: int,
    index: int,
    columns: int,
    pitch: int,
    font: str,
    vocabulary: Names,
    top: int,
    caption: str | None = None,
    include_key: bool = False,
) -> None:
    x, y = grid_position(index, columns, pitch, top)
    master_button(
        parent,
        name,
        pick_caption(name, vocabulary) if caption is None else caption,
        x,
        y,
        pitch - 4,
        SMALL_BUTTON_HEIGHT,
        function_id=function_id,
        include_key=include_key,
        font=font,
    )
