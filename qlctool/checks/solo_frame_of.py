"""The SoloFrame a console widget sits in, the nearest one up the tree."""

from lxml import etree

from ..localname import localname


def solo_frame_of(widget: etree._Element) -> etree._Element | None:
    """The nearest enclosing SoloFrame of `widget`, or None."""
    current = widget.getparent()
    while current is not None and localname(current) != "SoloFrame":
        current = current.getparent()
    return current
