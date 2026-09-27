"""The engine's Autostart function id, when the workspace declares one."""

from lxml import etree

from ..find_local import find_local
from ..findall_local import findall_local


def startup_function(root: etree._Element) -> int | None:
    for element in findall_local(root, "Engine"):
        startup = find_local(element, "Autostart")
        if startup is not None and startup.text and startup.text.isdigit():
            return int(startup.text)
    return None
