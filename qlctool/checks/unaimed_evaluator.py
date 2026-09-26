"""Whether some instant of a set of running functions leaves a head unaimed.

The instant rules' question (`instant_evaluator`) asked of position: a
Collection starts every member at once, so it leaves a head unaimed only when
every member can; a Chaser plays one step at a time, so any step that leaves
it unaimed is an instant that does. A stopped hook plays nothing. Memoised per
node, head and the stopped hooks that node can reach, like the instant
evaluator, because every state and pick asks about the same subtrees.

A floor a Collection starts first (`static_floors`) aims a head only while no
later member that still runs writes it: under one, it plays no part
(`floor_overridden`, 2026-09-27).
"""

from collections.abc import Collection

from .aims_head import aims_head
from .floor_overridden import floor_overridden
from .show_graph import CONCURRENT, ShowGraph
from .static_floors import static_floors


class UnaimedEvaluator:
    """Answer "can this instant leave that head unaimed" for one immutable graph."""

    def __init__(
        self, graph: ShowGraph, groups: dict[int, tuple[int, ...]], states: Collection[int]
    ) -> None:
        self._graph = graph
        self._groups = groups
        self._states = states
        self._memo: dict[tuple[int, int, frozenset[int], frozenset[int]], bool] = {}
        self._floors: dict[int, frozenset[int]] = {}

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
        elif self._graph.kind(function_id) == CONCURRENT:
            floors = self._floors_of(function_id)
            result = all(
                self._node(m, fixture_id, stopped, seen | {function_id})
                or (
                    m in floors
                    and floor_overridden(
                        self._graph, self._groups, members[i + 1 :], fixture_id, stopped
                    )
                )
                for i, m in enumerate(members)
            )
        else:
            result = any(self._node(m, fixture_id, stopped, seen | {function_id}) for m in members)
        self._memo[key] = result
        return result

    def _floors_of(self, collection_id: int) -> frozenset[int]:
        floors = self._floors.get(collection_id)
        if floors is None:
            floors = static_floors(self._graph, self._groups, collection_id, self._states)
            self._floors[collection_id] = floors
        return floors
