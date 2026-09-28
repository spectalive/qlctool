"""Widgets whose absolute position spills past the console's own canvas."""

from lxml import etree

from ..find_local import find_local
from ..localname import localname
from .positioned_widgets import positioned_widgets


def off_canvas_widgets(
    frame: etree._Element, canvas: tuple[int, int]
) -> list[tuple[str, int, int]]:
    """(widget label, its right edge, its bottom edge) for each widget off canvas."""
    width, height = canvas
    found: list[tuple[str, int, int]] = []
    for widget, left, top in positioned_widgets(frame):
        state = find_local(widget, "WindowState")
        if state is None:
            continue
        right = left + int(state.attrib["Width"])
        bottom = top + int(state.attrib["Height"])
        if right > width or bottom > height:
            found.append((widget.attrib.get("Caption", "") or localname(widget), right, bottom))
    return found
