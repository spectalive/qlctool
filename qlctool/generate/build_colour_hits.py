"""The JUGAR page's colour-hit strip: one flash button per palette colour."""

from collections.abc import Callable, Mapping

from lxml import etree

from ..argb import argb_from_rgb
from ..names.names import Names
from ..vc.build_button import FLASH
from .play_page_layout import GAP, HEADER, LEFT, SMALL_BUTTON_HEIGHT, WIDTH
from .readable_foreground import readable_foreground


def build_colour_hits(
    outer: etree._Element,
    button: Callable[..., object],
    frame: Callable[..., etree._Element],
    colour_flash_ids: Mapping[str, int],
    page: int,
    title_font: str,
    small_font: str,
    palette: Mapping[str, tuple[int, int, int]],
    vocabulary: Names,
) -> None:
    hits = frame(
        outer,
        vocabulary.display("colour_hits"),
        LEFT,
        152,
        WIDTH,
        70,
        page=page,
        font=title_font,
    )
    pitch = (WIDTH - 2 * GAP) // max(len(colour_flash_ids), 1)
    for index, (colour_name, function_id) in enumerate(colour_flash_ids.items()):
        colour = palette[colour_name]
        button(
            hits,
            function_id,
            colour_name.upper(),
            GAP + index * pitch,
            HEADER,
            pitch - 4,
            SMALL_BUTTON_HEIGHT,
            action=FLASH,
            flash_override=True,
            flash_force_ltp=True,
            background=str(argb_from_rgb(colour)),
            foreground=str(argb_from_rgb(readable_foreground(colour))),
            font=small_font,
        )
