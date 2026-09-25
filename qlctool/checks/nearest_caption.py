"""The caption a console element is found by."""

from lxml import etree

from ..xmlutil import localname


def nearest_caption(element: etree._Element) -> str:
    """The nearest widget with a caption: what somebody would look for on the console."""
    for ancestor in element.iterancestors():
        if ancestor.get("Caption"):
            return ancestor.get("Caption", "")
    return localname(element)
