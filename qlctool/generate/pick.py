"""One manual pick. `mark` is the family's glyph, so a full page of picks
still says which family each tile belongs to (owner, 2026-09-22).
"""

from collections.abc import Callable, Mapping

from lxml import etree

from ..names.names import Names
from .grid_position import grid_position
from .pick_caption import pick_caption
from .play_page_layout import SMALL_BUTTON_HEIGHT


def pick(
    button: Callable[..., object],
    parent: etree._Element,
    names: Mapping[int, str],
    function_id: int,
    index: int,
    columns: int,
    pitch: int,
    font: str,
    vocabulary: Names,
    top: int,
    mark: str = "",
) -> None:
    x, y = grid_position(index, columns, pitch, top)
    caption = pick_caption(names.get(function_id, ""), vocabulary)
    button(
        parent,
        function_id,
        f"{mark} {caption}" if mark else caption,
        x,
        y,
        pitch - 4,
        SMALL_BUTTON_HEIGHT,
        font=font,
    )
