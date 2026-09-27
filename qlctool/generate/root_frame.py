"""The Virtual Console's root frame, where the live console is built.

Moved verbatim out of `live_console` (2026-09-27 split).
"""

from lxml import etree

from ..find_local import find_local


def root_frame(root: etree._Element) -> etree._Element:
    console = find_local(root, "VirtualConsole")
    if console is None:
        raise ValueError("workspace has no <VirtualConsole>")
    frame = find_local(console, "Frame")
    if frame is None:
        raise ValueError("Virtual Console has no root <Frame>")
    return frame
