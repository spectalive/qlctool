"""At least one written value actually strobes its channel."""

from .read_only_driven import ReadOnlyDriven
from .show_graph import ShowGraph
from .strobe_written import strobe_capable_offsets
from .value_strobes import value_strobes


def any_strobing_write(graph: ShowGraph, written: ReadOnlyDriven) -> bool:
    for fixture_id, pairs in written.items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        capable = strobe_capable_offsets(capability)
        for offset, value in pairs.items():
            if value is None or offset not in capable:
                continue
            if value_strobes(capable[offset], value):
                return True
    return False
