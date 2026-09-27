"""The functions of every Toggle button, keyed by the solo frame holding it.

Buttons outside any solo frame are keyed by None, which makes them count
as "elsewhere" for every frame.
"""

from lxml import etree

from ..find_local import find_local
from ..iter_local import iter_local
from ..vc.build_button import NO_FUNCTION
from .solo_frame_ancestor import solo_frame_ancestor


def toggle_functions_by_frame(root: etree._Element) -> dict[etree._Element | None, set[int]]:
    found: dict[etree._Element | None, set[int]] = {}
    for button in iter_local(root, "Button"):
        action = find_local(button, "Action")
        if action is not None and (action.text or "").strip() not in ("", "Toggle"):
            continue
        function = find_local(button, "Function")
        if function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if function_id == NO_FUNCTION:
            continue
        found.setdefault(solo_frame_ancestor(button), set()).add(function_id)
    return found
