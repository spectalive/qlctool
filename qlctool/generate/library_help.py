"""Page 4's help lines: what the page holds, because nobody reads a manual at a venue.

Moved verbatim out of `page_library` (2026-09-27 split). `label` is the
console's own widget closure, so the widget ids come out in the order they
always did.
"""

from collections.abc import Callable

from lxml import etree

from ..names.names import Names
from .console_layout import HELP_FONT, LEFT_WIDTH, LEFT_X, LIBRARY_SEPARATOR, PAGE_LIBRARY
from .generated_builtins import GeneratedBuiltins
from .library_help_lines import library_help_lines


def library_help(
    outer: etree._Element,
    label: Callable[..., etree._Element],
    builtins: GeneratedBuiltins,
    has_panels: bool,
    has_mixes: bool,
    has_matrices: bool,
    vocabulary: Names,
) -> None:
    """A page of 180 buttons otherwise reads as something somebody is
    supposed to be using; `library_help_lines` picks the lines.
    """
    lines = library_help_lines(
        bool(builtins.scene_ids),
        has_panels,
        has_mixes=has_mixes,
        has_matrices=has_matrices,
    )
    for index, line in enumerate(lines):
        label(
            outer,
            LIBRARY_SEPARATOR
            if line is None
            else vocabulary.render(line, count=len(builtins.scene_ids)),
            LEFT_X,
            410 + index * 26,
            LEFT_WIDTH,
            24,
            page=PAGE_LIBRARY,
            font=HELP_FONT,
        )
