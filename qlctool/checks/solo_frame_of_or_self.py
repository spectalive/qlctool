"""The nearest SoloFrame including the widget itself, or None outside one."""

from lxml import etree

from ..localname import localname


def solo_frame_of_or_self(widget: etree._Element | None) -> etree._Element | None:
    current = widget
    while current is not None:
        if localname(current) == "SoloFrame":
            return current
        current = current.getparent()
    return None
