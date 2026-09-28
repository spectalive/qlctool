"""A saved workspace's functions by id, to tell whether it is the show QLC+ is running."""

from lxml import etree

from ..iter_local import iter_local
from ..localname import localname


def workspace_functions(root: etree._Element) -> dict[int, str]:
    """Id to name of every function in the workspace's engine."""
    return {
        int(element.get("ID", "-1")): element.get("Name", "")
        for element in iter_local(root, "Function")
        if "ID" in element.attrib
        and (parent := element.getparent()) is not None
        and localname(parent) == "Engine"
    }
