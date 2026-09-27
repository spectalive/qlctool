"""Button widget ID -> the SoloFrame it sits directly inside, if any."""

from lxml import etree

from ..xmlutil import localname
from .console_widget_tags import WIDGETS


def solo_frame_membership(console: etree._Element) -> dict[str, etree._Element]:
    membership: dict[str, etree._Element] = {}

    def walk(node: etree._Element, solo_ancestor: etree._Element | None) -> None:
        for child in node:
            name = localname(child)
            if name not in WIDGETS:
                continue
            if name == "Button" and solo_ancestor is not None and "ID" in child.attrib:
                membership[str(child.attrib["ID"])] = solo_ancestor
            if name in ("Frame", "SoloFrame"):
                walk(child, child if name == "SoloFrame" else solo_ancestor)

    walk(console, None)
    return membership
