"""How a finding names a console frame that has no caption."""

from lxml import etree

from ..xmlutil import localname
from .phrase import Phrase


def untitled_frame(frame: etree._Element) -> Phrase:
    """`marco 12` / `marco solo 12`, `frame 12` / `solo frame 12`: by kind and id."""
    fields = {"id": frame.get("ID")}
    if localname(frame) == "SoloFrame":
        return Phrase("empty_frame_untitled_solo", fields)
    return Phrase("empty_frame_untitled", fields)
