"""Whether some instant of a set of running functions leaves a head unaimed.

The instant rules' question (`instant_evaluator`) asked of position: a
Collection starts every member at once, so it leaves a head unaimed only when
every member can; a Chaser plays one step at a time, so any step that leaves
it unaimed is an instant that does. A stopped hook plays nothing. Memoised per
node, head and the stopped hooks that node can reach, like the instant
evaluator, because every state and pick asks about the same subtrees.
"""

from .aims_head import aims_head
from .show_graph import CONCURRENT, ShowGraph


class UnaimedEvaluator:
    """Answer "can this instant leave that head unaimed" for one immutable graph."""

    def __init__(self, graph: ShowGraph, groups: dict[int, tuple[int, ...]]) -> None:
        self._graph = graph
        self._groups = groups
        self._memo: dict[tuple[int, int, frozenset[int], frozenset[int]], bool] = {}

    def can_leave(self, roots: tuple[int, ...], fixture_id: int, stopped: frozenset[int]) -> bool:
        """True when the `roots`, running together, can leave `fixture_id` unaimed."""
        return all(self._node(root, fixture_id, stopped, frozenset()) for root in roots)

    def _node(
        self, function_id: int, fixture_id: int, stopped: frozenset[int], seen: frozenset[int]
    ) -> bool:
        below = self._graph.descendants(function_id)
        key = (function_id, fixture_id, stopped & below, seen & below)
        cached = self._memo.get(key)
        if cached is not None:
            return cached
        members = self._graph.members.get(function_id, ())
        if function_id not in self._graph.functions or function_id in stopped | seen:
            result = True
        elif not members:
            result = not aims_head(self._graph, self._groups, function_id, fixture_id)
        else:
            parts = (self._node(m, fixture_id, stopped, seen | {function_id}) for m in members)
            result = all(parts) if self._graph.kind(function_id) == CONCURRENT else any(parts)
        self._memo[key] = result
        return result
