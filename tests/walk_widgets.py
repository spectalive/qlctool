"""Every widget under a console frame, with its absolute position on the canvas."""

from qlctool.find_local import find_local
from qlctool.localname import localname

WIDGET_TAGS = {
    "Frame",
    "SoloFrame",
    "Button",
    "Label",
    "Slider",
    "XYPad",
    "SpeedDial",
    "AudioTriggers",
    "Matrix",
    "Clock",
}


def walk_widgets(widget, x=0, y=0):
    """Every widget with its absolute position on the canvas."""
    for child in widget:
        if localname(child) not in WIDGET_TAGS:
            continue
        state = find_local(child, "WindowState")
        cx = x + int(state.attrib["X"])
        cy = y + int(state.attrib["Y"])
        yield child, cx, cy
        yield from walk_widgets(child, cx, cy)
