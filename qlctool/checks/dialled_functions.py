"""Function ids some speed dial can re-time, and that can answer one."""

from lxml import etree

from ..find_local import find_local
from ..findall_local import findall_local
from ..iter_local import iter_local


def dialled_functions(root: etree._Element) -> set[int]:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return set()
    dialled: set[int] = set()
    for dial in iter_local(console, "SpeedDial"):
        for function in findall_local(dial, "Function"):
            text = (function.text or "").strip()
            if text.isdigit():
                dialled.add(int(text))
    return dialled
