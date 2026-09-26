"""The offsets of one fixture QLC+ merges HTP, as the show graph read them.

The patch can move a channel either way (`<ForcedLTP>`, `<ForcedHTP>`), so the
definition's Intensity group is only the default (`htp_offsets`). A graph
built without a patch - a hand-made one in a test - falls back to it.
"""

from .htp_offsets import INTENSITY_GROUP
from .show_graph import ShowGraph


def merged_htp(graph: ShowGraph, fixture_id: int) -> frozenset[int]:
    """The fixture's HTP offsets; none for a fixture the graph has no definition of."""
    if fixture_id in graph.htp:
        return graph.htp[fixture_id]
    capability = graph.capabilities.get(fixture_id)
    if capability is None:
        return frozenset()
    return frozenset(
        offset
        for offset, group in enumerate(capability.groups_by_offset)
        if group == INTENSITY_GROUP
    )
