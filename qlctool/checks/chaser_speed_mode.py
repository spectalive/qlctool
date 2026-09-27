"""A chaser's FadeIn speed mode: Common for every step, or PerStep."""

from lxml import etree

from ..xmlutil import find_local


def chaser_speed_mode(function: etree._Element) -> str:
    modes = find_local(function, "SpeedModes")
    return modes.attrib.get("FadeIn", "Common") if modes is not None else "Common"
