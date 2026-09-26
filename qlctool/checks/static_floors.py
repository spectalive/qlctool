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

Only LTP channels: an Intensity channel is merged HTP and zeroed every tick, so
order means nothing there. The channel groups come from the definitions; the
generator writes no `<ForcedHTP>` on a wheel or a position.
"""

from .show_graph import ShowGraph, reach

INTENSITY_GROUP = "Intensity"


def static_floors(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], collection_id: int
) -> frozenset[int]:
    """Scene members that write only LTP channels, under a later member and no earlier one."""
    if graph.kind(collection_id) != "Collection":
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
            (capability := graph.capabilities.get(f)) is None
            or capability.groups_by_offset[o] == INTENSITY_GROUP
            for f, o in channels[index]
        ):
            continue
        earlier = set().union(*channels[:index])
        later = set().union(*channels[index + 1 :])
        if channels[index] & later and not channels[index] & earlier:
            found.add(member)
    return frozenset(found)
