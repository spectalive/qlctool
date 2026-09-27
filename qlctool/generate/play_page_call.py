"""Call page 2 (JUGAR) only where a play family was built for it.

Moved verbatim out of `generate_live_console` (2026-09-27 split): the guard
and the call are unchanged, only the page's fixed page number and fonts move
here with them.
"""

from collections.abc import Callable, Mapping, Sequence

from lxml import etree

from ..names.names import Names
from .build_play_page import build_play_page
from .console_layout import BIG_FONT, PAGE_PLAY, SMALL_FONT, TITLE_FONT
from .generated_play_wrappers import GeneratedPlayWrappers


def play_page_call(
    outer: etree._Element,
    button: Callable[..., object],
    master_button: Callable[..., object],
    frame: Callable[..., etree._Element],
    label: Callable[..., object],
    names: Mapping[int, str],
    master: Mapping[str, int],
    play_wrappers: GeneratedPlayWrappers | None,
    colour_flash_ids: Mapping[str, int],
    flash_functions: Sequence[str],
    palette: Mapping[str, tuple[int, int, int]] | None,
    vocabulary: Names | None,
) -> None:
    """A rig with no play wrapper gets no JUGAR page."""
    if play_wrappers is None:
        return
    build_play_page(
        outer,
        button,
        master_button,
        frame,
        label,
        names,
        master,
        play_wrappers,
        colour_flash_ids,
        flash_functions,
        PAGE_PLAY,
        TITLE_FONT,
        BIG_FONT,
        SMALL_FONT,
        palette=palette,
        vocabulary=vocabulary,
    )
