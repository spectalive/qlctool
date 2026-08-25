"""Build a Virtual Console <Frame> or <SoloFrame>, optionally multipage.

A plain frame only groups widgets. A solo frame also enforces one-at-a-time:
whenever a widget inside it starts a function, every other widget in it stops
its own - VCSoloFrame::slotWidgetFunctionStarting. That is what a bank of
colours wants and what a function and its own members must never share, because
the member starting is what kills the parent.

Multipage turns the frame into a stack of pages, each child on the page named by
its own `Page` attribute, with the page arrows in the frame header.
"""

from lxml import etree

from ..constants import QLC_NS
from .appearance import build_appearance
from .window_state import build_window_state


def build_frame(
    parent: etree._Element,
    widget_id: int,
    caption: str,
    x: int,
    y: int,
    width: int,
    height: int,
    solo: bool = False,
    pages: int = 1,
    next_page_key: str | None = None,
    previous_page_key: str | None = None,
) -> etree._Element:
    """Append a frame to parent and return it, ready for child widgets."""
    tag = "SoloFrame" if solo else "Frame"
    frame = etree.SubElement(parent, f"{{{QLC_NS}}}{tag}")
    frame.set("Caption", caption)
    frame.set("ID", str(widget_id))

    build_appearance(frame, frame_style="Sunken")
    build_window_state(frame, x, y, width, height)

    children = [
        ("AllowChildren", "True"),
        ("AllowResize", "True"),
        ("ShowHeader", "True"),
        ("ShowEnableButton", "False"),
    ]
    if solo:
        children.append(("Mixing", "False"))
        # Only stop the function of a button somebody actually pressed. Without
        # this a chaser stepping through the looks in the frame makes every step
        # cut the one before it dead, because each step's button reports its
        # function starting - VCButton::notifyFunctionStarting.
        children.append(("ExcludeMonitored", "True"))
    children += [("Collapsed", "False"), ("Disabled", "False")]
    for name, value in children:
        etree.SubElement(frame, f"{{{QLC_NS}}}{name}").text = value

    if pages > 1:
        multipage = etree.SubElement(frame, f"{{{QLC_NS}}}Multipage")
        multipage.set("PagesNum", str(pages))
        multipage.set("CurrentPage", "0")
        for name, key in (
            ("Next", next_page_key),
            ("Previous", previous_page_key),
        ):
            if key is None:
                continue
            element = etree.SubElement(frame, f"{{{QLC_NS}}}{name}")
            etree.SubElement(element, f"{{{QLC_NS}}}Key").text = key
        etree.SubElement(frame, f"{{{QLC_NS}}}PagesLoop").text = "True"

    return frame
