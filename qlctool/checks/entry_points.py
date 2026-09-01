"""The functions somebody can actually start: every button on the console.

A show is only as correct as the things a person is able to press. Checking
every function in the workspace would drown a report in scenes that only ever
run as one step of one chaser, where being dark on their own is the point. What
matters is the set of entry points - the buttons - because each of those is a
promise about what the room will do.
"""

from lxml import etree

from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, iter_local


def entry_points(root: etree._Element) -> dict[int, str]:
    """Function id -> the caption of the button that starts it.

    A button with no function - the blackout and panic actions - is skipped: it
    stops functions rather than starting one.
    """
    console = find_local(root, "VirtualConsole")
    if console is None:
        return {}
    found: dict[int, str] = {}
    for button in iter_local(console, "Button"):
        function = find_local(button, "Function")
        if function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if function_id == NO_FUNCTION:
            continue
        found.setdefault(function_id, button.attrib.get("Caption", "") or str(function_id))
    return found
