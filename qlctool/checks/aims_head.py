"""Whether one leaf function aims a moving head somewhere the room can use.

A head nothing writes sits at mid-travel - 127 on pan and tilt, QLC+'s
default - and mid-travel is not a place: the floor on a 7R, the wall behind
the stage on a wash (`movement_aim`). So a leaf aims a head when it writes both
its pan and its tilt and neither is left at mid-travel outside the family's
measured window: an EFX that moves the head from the start (`serial_waits`),
or a Scene with a value of its own. A Scene aiming below the window on
purpose - `Escenario`, on the stage rather than the crowd - is an aim; where
an EFX figure goes is `movement_window`'s question.
"""

from .. import roles
from ..audience_window import BEAM_WINDOW, WASH_WINDOW
from .rule_unaimed_movement import MID_TRAVEL
from .serial_waits import serial_waits
from .show_graph import ShowGraph


def aims_head(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int, fixture_id: int
) -> bool:
    """True when leaf `function_id` holds `fixture_id` on a pan and a tilt of its own."""
    capability = graph.capabilities.get(fixture_id)
    function = graph.functions.get(function_id)
    if capability is None or function is None:
        return False
    written = graph.driven(function_id, groups).get(fixture_id, {})
    window = BEAM_WINDOW if capability.has_role(roles.GOBO) else WASH_WINDOW
    axes = (
        ("pan", capability.offsets_for_role(roles.PAN)),
        ("tilt", capability.offsets_for_role(roles.TILT)),
    )
    for axis, offsets in axes:
        if not offsets or any(offset not in written for offset in offsets):
            return False
        for offset in offsets:
            value = written[offset]
            if value == MID_TRAVEL and not window.holds(value, 0, axis):
                return False
    if function.attrib.get("Type") == "EFX":
        return not serial_waits(function, fixture_id)
    return True
