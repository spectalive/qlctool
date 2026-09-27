"""Every channel a function can drive, through anything it starts.

`kinds` restricts which leaf function types count - "what does this look
*state* about colour" is a question about its Scenes, since a matrix paints
a group's pixels and can say nothing about a fixture that has none.

Values merge by the highest, because DMX does: QLC+ mixes intensity
channels HTP, so what the room sees from two sources on one channel is the
louder of them. `None` - an effect driving a channel to a value nobody can
predict - beats any number, since it may be anything at any moment.

Memoised on the graph, and handed out as a copy so a caller may write into
it: the rules ask this of the same functions some sixteen thousand times
per pass (2026-09-22).
"""

from .driven_channels import Driven
from .show_graph import ShowGraph
from .uncached_reach import uncached_reach


def reach(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    function_id: int,
    kinds: tuple[str, ...] | None = None,
) -> Driven:
    key = (function_id, kinds, graph.groups_key(groups))
    cached = graph.reach_cache.get(key)
    if cached is None:
        cached = uncached_reach(graph, groups, function_id, kinds)
        graph.reach_cache[key] = cached
    return {fixture_id: dict(pairs) for fixture_id, pairs in cached.items()}
