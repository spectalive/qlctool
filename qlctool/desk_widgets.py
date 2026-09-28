"""Every frame and widget under a workspace's console, in document order."""

from lxml import etree

from .desk_widget import DeskWidget
from .find_local import find_local
from .walk import walk


def desk_widgets(root: etree._Element) -> list[DeskWidget]:
    """Every frame and widget under the console, in document order."""
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    found: list[DeskWidget] = []
    walk(console, (), None, 0, found)
    return found
