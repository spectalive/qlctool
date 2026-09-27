"""What each key and pad channel presses among the Flash buttons forced LTP.

A key bound to several buttons presses them all at once: keys 1-0 hold the
same colour in every bank. Grouped by trigger - the keyboard key, or the
channel on the pad's input universe - the scenes of each trigger's buttons,
every trigger that presses the same set reported once.
"""

from lxml import etree

from ..pad_input_universe import pad_input_universe
from ..vc.build_button import NO_FUNCTION
from ..xmlutil import find_local, iter_local
from .bound_inputs import bound_inputs


def forced_flash_triggers(root: etree._Element) -> dict[tuple[str, str], frozenset[int]]:
    """("key", "1") or ("pad", "37040") -> function ids of the forced Flash buttons."""
    console = find_local(root, "VirtualConsole")
    if console is None:
        return {}
    pressed: dict[tuple[str, str], set[int]] = {}
    forced: dict[etree._Element, int] = {}
    for button in iter_local(console, "Button"):
        action = find_local(button, "Action")
        function = find_local(button, "Function")
        if action is None or (action.text or "").strip() != "Flash" or function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if action.get("ForceLTP") != "1" or function_id == NO_FUNCTION:
            continue
        forced[button] = function_id
        key = find_local(button, "Key")
        if key is not None and key.text:
            pressed.setdefault(("key", key.text), set()).add(function_id)
    for channel, widget in bound_inputs(root, pad_input_universe(root)):
        if widget in forced:
            pressed.setdefault(("pad", str(channel)), set()).add(forced[widget])
    found: dict[tuple[str, str], frozenset[int]] = {}
    for trigger, functions in pressed.items():
        if frozenset(functions) not in found.values():
            found[trigger] = frozenset(functions)
    return found
