"""Every function's name by id, as the console captions its buttons from them.

Moved verbatim out of `live_console` (2026-09-27 split).
"""

from ..localname import localname
from ..workspace import Workspace


def function_names(workspace: Workspace) -> dict[int, str]:
    return {
        int(f.attrib["ID"]): f.attrib.get("Name", "")
        for f in workspace.engine
        if localname(f) == "Function" and f.attrib.get("ID")
    }
