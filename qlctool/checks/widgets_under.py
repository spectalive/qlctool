"""Every widget under `parent`, at any depth, each visited exactly once."""

from collections.abc import Iterator

from lxml import etree

from ..xmlutil import localname
from .console_widget_tags import WIDGETS


def widgets_under(parent: etree._Element) -> Iterator[etree._Element]:
    """Every widget under `parent`, at any depth - each visited exactly once,
    so a containment check below can look at a widget's own direct children
    without walking the tree itself.
    """
    for child in parent:
        if localname(child) not in WIDGETS:
            continue
        yield child
        yield from widgets_under(child)
