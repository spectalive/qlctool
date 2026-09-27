"""A function's own FadeIn, the crossfade a scene or chaser step carries in."""

from lxml import etree

from ..find_local import find_local


def own_fade_in(function: etree._Element) -> int:
    speed = find_local(function, "Speed")
    return int(speed.attrib.get("FadeIn", "0")) if speed is not None else 0
