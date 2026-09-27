"""Whether the thing this button starts carries its own "pump shut".

A chaser alternating a fog step with an off step does - `Humo Auto` has run
the haze that way for years, and the pump closes again a step later whatever
anyone presses. A SingleShot burst does when its **last** step is the one
that closes it. A Collection is as safe as the member that does, so the
question recurses. A bare scene never does.
"""

from ..find_local import find_local
from .show_graph import ShowGraph
from .shuts_pump import shuts_pump


def clears_itself(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    function_id: int,
    held: dict[int, set[int]],
    seen: frozenset[int] = frozenset(),
) -> bool:
    if function_id in seen:
        return False
    seen = seen | {function_id}
    steps = graph.members.get(function_id, ())
    if not steps:
        return False
    function = graph.functions[function_id]
    order = find_local(function, "RunOrder")
    single = (
        function.attrib.get("Type") == "Chaser"
        and order is not None
        and (order.text or "").strip() == "SingleShot"
    )
    candidates = [steps[-1]] if single else list(steps)
    return any(
        shuts_pump(graph, groups, step, held) or clears_itself(graph, groups, step, held, seen)
        for step in candidates
    )
