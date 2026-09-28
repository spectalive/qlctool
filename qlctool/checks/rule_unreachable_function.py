"""A built function that nothing on the console can start.

2026-09-25: Vibra without its smoke machines carried the panels' vertical-smoke
light chaser with no button to start it. The generator was fixed (the light is
built only where a column is patched), and this rule is what would have seen
it: a function is reached by a console widget that names it (a button, a
slider, a matrix, a cue list, a clock, an audio bar, an XY pad preset, a speed
dial) or, from one of those, by a Collection or Chaser step, a Sequence's
bound scene or a Show track. What is left is built and can be started only
from the function manager, which nobody opens with the room full. An input
profile binds widgets, never functions, so a function the pad reaches is a
function a widget reaches.
"""

from lxml import etree

from ..find_local import find_local
from ..localname import localname
from .console_reference import console_reference
from .engine_reference import engine_reference
from .finding import WARNING, Finding
from .invalid_function_id import INVALID_ID

RULE_ID = "unreachable_function"


def check_unreachable_functions(root: etree._Element) -> list[Finding]:
    engine = find_local(root, "Engine")
    console = find_local(root, "VirtualConsole")
    functions: dict[int, etree._Element] = {}
    named: dict[int, set[int]] = {}
    for function in engine if engine is not None else ():
        if localname(function) != "Function" or not function.get("ID", "").isdigit():
            continue
        function_id = int(function.get("ID", ""))
        functions[function_id] = function
        named[function_id] = {
            int(raw)
            for element in function.iter()
            for _, raw in engine_reference(function, element, "")
            if raw.isdigit()
        }
    pending = [
        int(raw)
        for element in (console.iter() if console is not None else ())
        if (raw := console_reference(element)) is not None and raw != INVALID_ID and raw.isdigit()
    ]
    reached: set[int] = set()
    while pending:
        function_id = pending.pop()
        if function_id in reached:
            continue
        reached.add(function_id)
        pending.extend(named.get(function_id, ()))
    return [
        Finding(
            rule_id=RULE_ID,
            severity=WARNING,
            function=function.get("Name", str(function_id)),
            message_id="unreachable_function_unstarted",
            fields={"kind": function.get("Type", "")},
        )
        for function_id, function in sorted(functions.items())
        if function_id not in reached
    ]
