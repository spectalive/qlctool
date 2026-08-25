"""Build a Virtual Console <XYPad> that steers a set of moving fixtures.

Each fixture is listed with the slice of its pan and tilt range the pad covers -
0 to 1 is the whole range - so dragging the cursor writes pan and tilt on every
head at once. Fixtures without pan and tilt must not be listed: QLC+ would have
no axis to write.
"""

from collections.abc import Sequence

from lxml import etree

from ..constants import QLC_NS
from .appearance import build_appearance
from .window_state import build_window_state


def build_xy_pad(
    parent: etree._Element,
    widget_id: int,
    caption: str,
    x: int,
    y: int,
    width: int,
    height: int,
    fixture_ids: Sequence[int],
    position: tuple[int, int] = (127, 127),
) -> etree._Element:
    pad = etree.SubElement(parent, f"{{{QLC_NS}}}XYPad")
    pad.set("Caption", caption)
    pad.set("ID", str(widget_id))
    pad.set("InvertedAppearance", "0")

    build_window_state(pad, x, y, width, height)
    build_appearance(pad, frame_style="Sunken")

    for fixture_id in fixture_ids:
        fixture = etree.SubElement(pad, f"{{{QLC_NS}}}Fixture")
        fixture.set("ID", str(fixture_id))
        fixture.set("Head", "0")
        for axis_id in ("X", "Y"):
            axis = etree.SubElement(fixture, f"{{{QLC_NS}}}Axis")
            axis.set("ID", axis_id)
            axis.set("LowLimit", "0")
            axis.set("HighLimit", "1")
            axis.set("Reverse", "False")

    for name, value in (("Pan", position[0]), ("Tilt", position[1])):
        axis = etree.SubElement(pad, f"{{{QLC_NS}}}{name}")
        axis.set("Position", str(value))

    return pad
