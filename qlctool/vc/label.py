"""Build a Virtual Console <Label> - a caption placed on the console."""

from lxml import etree

from ..constants import QLC_NS
from .appearance import build_appearance
from .window_state import build_window_state


def build_label(
    parent: etree._Element,
    widget_id: int,
    caption: str,
    x: int,
    y: int,
    width: int,
    height: int,
) -> etree._Element:
    label = etree.SubElement(parent, f"{{{QLC_NS}}}Label")
    label.set("Caption", caption)
    label.set("ID", str(widget_id))
    build_window_state(label, x, y, width, height)
    build_appearance(label)
    return label
