"""A function's own crossfade, the longer of its FadeIn and FadeOut."""

from lxml import etree

from ..find_local import find_local


def function_fade(function: etree._Element) -> int:
    speed = find_local(function, "Speed")
    if speed is None:
        return 0
    return max(int(speed.attrib.get("FadeIn", 0)), int(speed.attrib.get("FadeOut", 0)))
