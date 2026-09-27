"""A widget that spills past its own parent frame's box, not just the canvas."""

from lxml import etree

from ..find_local import find_local
from ..xmlutil import localname
from .console_widget_tags import WIDGETS
from .widgets_under import widgets_under


def widgets_out_of_frame(frame: etree._Element) -> list[tuple[str, str, int, int, int, int]]:
    """(child label, parent frame caption, right, bottom, parent width, parent height).

    `off_canvas_widgets` only ever compares a widget's absolute position against
    the outer 1440x900 screen: a widget nested two frames deep can sit well
    inside that and still spill past the box of the frame meant to hold it,
    drawn clipped or over whatever sits below or beside that frame.

    Local coordinates, deliberately: a widget's <WindowState> X/Y is already
    relative to its own parent's top-left, and a multipage frame puts every
    page's widgets at those same local coordinates on purpose - two pages'
    buttons landing on top of each other there is normal, not a bug. Checking
    only against the immediate parent's own Width/Height, never against a
    sibling widget, is what keeps paging from reading as a collision.
    """
    found: list[tuple[str, str, int, int, int, int]] = []
    for widget in widgets_under(frame):
        state = find_local(widget, "WindowState")
        if state is None:
            continue
        width, height = int(state.attrib["Width"]), int(state.attrib["Height"])
        for child in widget:
            if localname(child) not in WIDGETS:
                continue
            child_state = find_local(child, "WindowState")
            if child_state is None:
                continue
            right = int(child_state.attrib["X"]) + int(child_state.attrib["Width"])
            bottom = int(child_state.attrib["Y"]) + int(child_state.attrib["Height"])
            if right > width or bottom > height:
                found.append(
                    (
                        child.attrib.get("Caption", "") or localname(child),
                        widget.attrib.get("Caption", ""),
                        right,
                        bottom,
                        width,
                        height,
                    )
                )
    return found
