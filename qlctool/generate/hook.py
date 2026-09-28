"""One master-button hook: a named function's own tile in a family frame."""

from collections.abc import Callable, Mapping

from lxml import etree

from ..argb_from_rgb import argb_from_rgb
from .grid_position import grid_position
from .play_page_layout import SMALL_BUTTON_HEIGHT
from .readable_foreground import readable_foreground

_HOOK_BACKGROUND = str(argb_from_rgb((20, 105, 82)))
_HOOK_FOREGROUND = str(argb_from_rgb(readable_foreground((20, 105, 82))))


def hook(
    master_button: Callable[..., object],
    parent: etree._Element,
    ids_by_name: Mapping[str, int],
    name: str,
    caption: str,
    index: int,
    columns: int,
    pitch: int,
    font: str,
    top: int,
    include_key: bool = False,
) -> None:
    x, y = grid_position(index, columns, pitch, top)
    master_button(
        parent,
        name,
        caption,
        x,
        y,
        pitch - 4,
        SMALL_BUTTON_HEIGHT,
        function_id=ids_by_name.get(name),
        include_key=include_key,
        background=_HOOK_BACKGROUND,
        foreground=_HOOK_FOREGROUND,
        font=font,
    )
