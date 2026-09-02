"""The console's latched layers: every Toggle button that is not a room state.

Three rules ask the same first question - which buttons stay on after the
finger leaves, on top of whatever state is running - because a latched layer
is the one kind of button that keeps writing after the operator has stopped
thinking about it. A Flash releases; a state replaces; a Toggle layer adds,
and keeps adding.
"""

from dataclasses import dataclass

from lxml import etree

from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, iter_local


@dataclass(frozen=True)
class LayerButton:
    caption: str
    function_id: int


def layer_buttons(root: etree._Element, states: set[int]) -> list[LayerButton]:
    """Every Toggle button whose function is not one of the room's states."""
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    found: list[LayerButton] = []
    seen: set[int] = set()
    for button in iter_local(console, "Button"):
        action = find_local(button, "Action")
        if action is not None and (action.text or "").strip() not in ("", "Toggle"):
            continue
        function = find_local(button, "Function")
        if function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if function_id == NO_FUNCTION or function_id in states or function_id in seen:
            continue
        seen.add(function_id)
        found.append(LayerButton(button.attrib.get("Caption", ""), function_id))
    return found
