"""The ARGB an RGBMatrix paints with, in either colour format QLC+ writes."""

from lxml import etree

from ..xmlutil import find_local, findall_local


def matrix_colour(function: etree._Element) -> int | None:
    mono = find_local(function, "MonoColor")
    text = (mono.text or "") if mono is not None else ""
    if text.isdigit():
        return int(text)
    for colour in findall_local(function, "Color"):
        text = colour.text or ""
        if colour.attrib.get("Index") == "0" and text.isdigit():
            return int(text)
    return None
