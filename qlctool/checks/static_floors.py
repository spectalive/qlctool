"""The Scenes a Collection starts first, under members that write over them.

On an LTP channel QLC+ 5 keeps the value of the fader written last in a tick,
and a fader is appended to its universe's list when its function first writes
(`Universe::requestFader`, `Universe::write`). A Collection starts its members
in order, a Chaser starts every step as a new function, and an EFX or a Scene
listed later requests its fader later. So a Scene listed before every other
member that writes its channels is overridden by each of them while they run,
and, still running, writes its values again the tick one of them stops.

Measured on :9995, 2026-09-27: a gobo-and-prism Scene and a pan/tilt Scene put
first in `Momento Fiesta` never showed under `Gobo Animacion` or the head
figures, and the tick `Gobo Shake` or `Circulo` was released they did (gobo 5
and shake 1, pan 40 and tilt 200), until the hook was pressed again and won
again. That is a floor, not a second opinion: the release of a latched pick
lands on it instead of on whatever the pick left (ruling D8).

Only LTP channels: an HTP channel is merged highest-takes-precedence and zeroed
every tick, so order means nothing there. Which channels are HTP is the patch's
answer, ForcedLTP and ForcedHTP included (`merged_htp`).

Only under a room state (2026-09-27 review, I-2): the floor is what a released
pick lands on, and a pick is released over a state. In any other Collection a
Scene hidden under a later member that writes its channels is still a look
nobody sees, and `collision` must go on saying so.
"""

from collections.abc import Collection

from .merged_htp import merged_htp
from .reach import reach
from .show_graph import ShowGraph


def static_floors(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    collection_id: int,
    states: Collection[int],
) -> frozenset[int]:
    """A state's Scene members that write only LTP channels, under a later member and no earlier one."""
    if collection_id not in states or graph.kind(collection_id) != "Collection":
        return frozenset()
    members = graph.members.get(collection_id, ())
    channels = [
        {(f, o) for f, pairs in reach(graph, groups, member).items() for o in pairs}
        for member in members
    ]
    found: set[int] = set()
    for index, member in enumerate(members):
        if graph.kind(member) != "Scene" or not channels[index]:
            continue
        if any(
            f not in graph.capabilities or o in merged_htp(graph, f) for f, o in channels[index]
        ):
            continue
        earlier = set().union(*channels[:index])
        later = set().union(*channels[index + 1 :])
        if channels[index] & later and not channels[index] & earlier:
            found.add(member)
    return frozenset(found)
