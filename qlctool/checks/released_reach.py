"""What a room state still drives once some of the functions it started stop.

A SoloFrame stops a hook when a pick starts, and a Toggle pick released by the
operator stops too; QLC+ 5 restarts nothing (`vcbutton.cpp`, `vcsoloframe.cpp`
has no restore). The instant after a release is therefore the state with every
function of the frame stopped, and with everything those functions started
stopped with them. Values merge by the highest, as `reach` does.
"""

from .driven_channels import Driven
from .merge import merge
from .show_graph import ShowGraph


def released_reach(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    state_id: int,
    stopped: frozenset[int],
) -> Driven:
    """Every channel the state drives through functions none of `stopped` is."""
    driven: Driven = {}
    seen: set[int] = set()
    stack = [state_id]
    while stack:
        current = stack.pop()
        if current in seen or current in stopped or current not in graph.functions:
            continue
        seen.add(current)
        members = graph.members.get(current, ())
        if members:
            stack.extend(members)
        else:
            written = graph.driven(current, groups)
            driven = merge(driven, {f: dict(pairs) for f, pairs in written.items()})
    return driven
