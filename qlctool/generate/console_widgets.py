"""Build the live console's four widget closures, in the order they always were.

Moved verbatim out of `generate_live_console` (2026-09-27 split): each closure
still comes from its own factory, only the four calls now live together.
"""

from collections.abc import Callable, Mapping

from lxml import etree

from .button_factory import button_factory
from .console_ids import ConsoleIds
from .frame_factory import frame_factory
from .generated_console import GeneratedConsole
from .label_factory import label_factory
from .master_button_factory import master_button_factory


def console_widgets(
    ids: ConsoleIds,
    console: GeneratedConsole,
    widget_of: dict[int, int],
    master: Mapping[str, int],
    keys: Mapping[str, str],
    flash: set[str],
    glyphs: Mapping[str, str],
    pad_colors: Mapping[str, tuple[int, int, int]],
    pad_bindings: Mapping[str, int],
) -> tuple[
    Callable[..., etree._Element],
    Callable[..., etree._Element],
    Callable[..., etree._Element],
    Callable[..., etree._Element | None],
]:
    """Return `button, frame, label, master_button`, built in that order."""
    button = button_factory(ids, console, widget_of)
    frame = frame_factory(ids, console)
    label = label_factory(ids, console)
    master_button = master_button_factory(
        button, master, keys, flash, glyphs, pad_colors, pad_bindings
    )
    return button, frame, label, master_button
