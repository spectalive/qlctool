"""Every Function under a workspace's Engine, keyed by its ID string."""

from qlctool.find_local import find_local
from qlctool.localname import localname


def functions_by_id_of_workspace(workspace):
    return {
        function.attrib.get("ID"): function
        for function in find_local(workspace.root, "Engine")
        if localname(function) == "Function"
    }
