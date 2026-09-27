"""The Y below every widget already placed in the console's root frame."""

from lxml import etree

from ..xmlutil import find_local


def first_free_y(frame: etree._Element) -> int:
    bottom = 0
    for child in frame:
        state = find_local(child, "WindowState")
        if state is None:
            continue
        bottom = max(
            bottom,
            int(state.attrib.get("Y", "0")) + int(state.attrib.get("Height", "0")),
        )
    return bottom
