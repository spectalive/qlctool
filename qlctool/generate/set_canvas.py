"""Write the console's canvas size into the workspace's Virtual Console properties.

Moved verbatim out of `live_console` (2026-09-27 split).
"""

from lxml import etree

from ..find_local import find_local


def set_canvas(root: etree._Element, canvas: tuple[int, int]) -> None:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return
    properties = find_local(console, "Properties")
    if properties is None:
        return
    size = find_local(properties, "Size")
    if size is None:
        return
    size.set("Width", str(canvas[0]))
    size.set("Height", str(canvas[1]))
