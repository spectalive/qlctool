"""The nearest SoloFrame above a Toggle button, walking from its parent."""

from lxml import etree

from ..localname import localname


def solo_frame_ancestor(widget: etree._Element) -> etree._Element | None:
    current = widget.getparent()
    while current is not None:
        if localname(current) == "SoloFrame":
            return current
        current = current.getparent()
    return None
