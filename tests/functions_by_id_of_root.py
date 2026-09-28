"""Every Function under a root's Engine, keyed by its integer ID."""

from qlctool.find_local import find_local
from qlctool.localname import localname


def functions_by_id_of_root(root):
    return {
        int(function.attrib["ID"]): function
        for function in find_local(root, "Engine")
        if localname(function) == "Function" and "ID" in function.attrib
    }
