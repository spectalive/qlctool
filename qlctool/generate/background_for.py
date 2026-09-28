"""Colour a button by the palette colour its function is named after."""

from lxml import etree

from ..argb_from_rgb import argb_from_rgb
from ..palette import PALETTE
from ..vc.build_appearance import DEFAULT


def background_for(function: etree._Element, color_by_name: bool) -> str:
    if not color_by_name:
        return DEFAULT
    name = function.attrib.get("Name", "")
    for color_name, rgb in PALETTE.items():
        if name.endswith(color_name):
            return str(argb_from_rgb(rgb))
    return DEFAULT
