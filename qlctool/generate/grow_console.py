"""Keep the console canvas at least as tall as what was just laid out."""

from typing import cast

from lxml import etree

from ..find_local import find_local


def grow_console(root: etree._Element, needed_height: int) -> None:
    # A caller of this generator has already resolved the console (`root_frame`
    # raises when there is none), so it is never actually None here.
    console = cast(etree._Element, find_local(root, "VirtualConsole"))
    properties = find_local(console, "Properties")
    if properties is None:
        return
    size = find_local(properties, "Size")
    if size is None:
        return
    if int(size.attrib.get("Height", "0")) < needed_height:
        size.set("Height", str(needed_height))
