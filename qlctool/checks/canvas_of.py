"""The console canvas a workspace declares, which widgets must stay inside."""

from lxml import etree

from .default_canvas import DEFAULT_CANVAS


def canvas_of(root: etree._Element) -> tuple[int, int]:
    from ..xmlutil import find_local

    console = find_local(root, "VirtualConsole")
    properties = find_local(console, "Properties") if console is not None else None
    size = find_local(properties, "Size") if properties is not None else None
    if size is None:
        return DEFAULT_CANVAS
    return int(size.attrib.get("Width", DEFAULT_CANVAS[0])), int(
        size.attrib.get("Height", DEFAULT_CANVAS[1])
    )
