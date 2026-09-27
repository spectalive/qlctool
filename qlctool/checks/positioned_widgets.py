"""Every console widget under one, with its absolute canvas position."""

from collections.abc import Iterator

from lxml import etree

from ..xmlutil import find_local, localname
from .console_widget_tags import WIDGETS


def positioned_widgets(
    widget: etree._Element, x: int = 0, y: int = 0
) -> Iterator[tuple[etree._Element, int, int]]:
    for child in widget:
        if localname(child) not in WIDGETS:
            continue
        state = find_local(child, "WindowState")
        if state is None:
            continue
        left = x + int(state.attrib["X"])
        top = y + int(state.attrib["Y"])
        yield child, left, top
        yield from positioned_widgets(child, left, top)
