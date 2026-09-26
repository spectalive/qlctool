"""Whether a family pick writes nothing that decides if a fixture is lit.

`rule_pick_darkens` asks, for every pick of a family frame and every room
state, which fixtures the instant (state, pick) colours while its dimmer or
shutter is left dark. A pick that writes no colour, dimmer or shutter channel
on any fixture - a movement figure, a gobo, a prism - adds nothing to that
instant: its every channel state is the evaluator's neutral one, and HTP with
the neutral state is the identity. Its answer is then the state's own with
the frame's hooks stopped, the same for every such pick of the frame
(2026-09-26, round G: the rule was 40% of a check, most of it movement picks
asking the same question again).

Strobe channels count whole, open range or not: a superset of the shutters
the rule reads, so a pick is never taken for neutral when it is not.
"""

from .. import roles
from .color_roles import COLOUR
from .show_graph import ShowGraph, reach

_LIGHT_ROLES = (*COLOUR, roles.DIMMER, roles.STROBE)


def pick_leaves_light_alone(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], pick_id: int
) -> bool:
    """True when the pick writes no colour, dimmer or strobe channel of any fixture."""
    for fixture_id, written in reach(graph, groups, pick_id).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        for role in _LIGHT_ROLES:
            if any(offset in written for offset in capability.offsets_for_role(role)):
                return False
    return True
