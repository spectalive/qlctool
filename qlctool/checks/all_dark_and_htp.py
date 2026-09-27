"""A step whose only claim to darkness is zeros on Intensity channels."""

from .. import roles
from .lit import lit
from .reach import reach
from .show_graph import ShowGraph

INTENSITY_GROUP = "Intensity"


def all_dark_and_htp(graph: ShowGraph, groups: dict[int, tuple[int, ...]], step_id: int) -> bool:
    """A step whose only claim to darkness is zeros on Intensity channels.

    A shutter or strobe channel written is a way to go dark that HTP cannot
    veto, so a step that drives one is not this shape. Any other LTP channel
    it parks (a panel's mode, say) darkens nothing and is ignored.
    """
    wrote = False
    for fixture_id, written in reach(graph, groups, step_id).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        for offset, value in written.items():
            if capability.roles_by_offset[offset] == roles.STROBE:
                return False
            if capability.groups_by_offset[offset] != INTENSITY_GROUP:
                continue
            if lit(value):
                return False
            wrote = True
    return wrote
