"""The Button on the console pointed at a given function ID."""

from qlctool.find_local import find_local
from qlctool.localname import localname


def button_of(workspace, function_id):
    return next(
        b
        for b in workspace.root.iter()
        if localname(b) == "Button"
        and (function := find_local(b, "Function")) is not None
        and function.attrib.get("ID") == str(function_id)
    )
