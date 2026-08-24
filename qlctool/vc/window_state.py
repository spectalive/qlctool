"""Build the <WindowState> that places a Virtual Console widget on the canvas."""

from lxml import etree

from ..constants import QLC_NS


def build_window_state(
    parent: etree._Element, x: int, y: int, width: int, height: int
) -> etree._Element:
    state = etree.SubElement(parent, f"{{{QLC_NS}}}WindowState")
    state.set("Visible", "True")
    state.set("X", str(x))
    state.set("Y", str(y))
    state.set("Width", str(width))
    state.set("Height", str(height))
    return state
