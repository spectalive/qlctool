"""Build a Virtual Console <SoloFrame> - a group where one button wins.

Solo is what a look group wants: pressing another colour releases the previous
one, instead of stacking every scene on top of each other. Children are appended
by the caller after this returns.
"""

from lxml import etree

from ..constants import QLC_NS
from .appearance import build_appearance
from .window_state import build_window_state


def build_solo_frame(
    parent: etree._Element,
    widget_id: int,
    caption: str,
    x: int,
    y: int,
    width: int,
    height: int,
) -> etree._Element:
    """Append a <SoloFrame> to parent and return it, ready for buttons."""
    frame = etree.SubElement(parent, f"{{{QLC_NS}}}SoloFrame")
    frame.set("Caption", caption)
    frame.set("ID", str(widget_id))

    build_appearance(frame, frame_style="Sunken")
    build_window_state(frame, x, y, width, height)
    for name, value in (
        ("AllowChildren", "True"),
        ("AllowResize", "True"),
        ("ShowHeader", "True"),
        ("ShowEnableButton", "False"),
        ("Mixing", "False"),
        ("Collapsed", "False"),
        ("Disabled", "False"),
    ):
        etree.SubElement(frame, f"{{{QLC_NS}}}{name}").text = value
    return frame
