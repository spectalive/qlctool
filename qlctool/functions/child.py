"""Append a namespaced QLC+ workspace child element carrying a text value."""

from lxml import etree

from ..constants import QLC_NS


def child(parent: etree._Element, name: str, value: object) -> etree._Element:
    element = etree.SubElement(parent, f"{{{QLC_NS}}}{name}")
    element.text = str(value)
    return element
