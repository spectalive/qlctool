"""Walk the Virtual Console tree, collecting one DeskWidget per element."""

from lxml import etree

from .desk_widgets import FRAME_TAGS, WIDGET_TAGS, DeskWidget
from .localname import localname
from .widget import widget as _widget


def walk(
    parent: etree._Element,
    frames: tuple[int, ...],
    solo: int | None,
    page: int,
    found: list[DeskWidget],
) -> None:
    for element in parent:
        tag = localname(element)
        if tag not in FRAME_TAGS and tag not in WIDGET_TAGS:
            continue
        widget_page = int(element.attrib.get("Page", page))
        widget = _widget(element, tag, frames, solo, widget_page)
        found.append(widget)
        if tag in FRAME_TAGS:
            walk(
                element,
                (*frames, widget.id),
                widget.id if tag == "SoloFrame" else solo,
                widget_page,
                found,
            )
