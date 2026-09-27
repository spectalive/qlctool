"""Every written channel is a strobe-role channel, on every fixture."""

from .. import roles
from .read_only_driven import ReadOnlyDriven
from .show_graph import ShowGraph


def all_strobe_writes(graph: ShowGraph, written: ReadOnlyDriven) -> bool:
    for fixture_id, pairs in written.items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            return False
        strobe_offsets = set(capability.offsets_for_role(roles.STROBE))
        if not set(pairs) <= strobe_offsets:
            return False
    return True
