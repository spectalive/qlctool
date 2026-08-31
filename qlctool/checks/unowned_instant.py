"""Is there an instant where this fixture is lit and nobody owns this channel?

`reach` merges everything a state can drive through anything it starts, at any
step. That is the right unit for "can these two fight over a channel", and the
wrong unit for "is somebody owning this channel *right now*". A chaser's steps
are alternatives, so a value written by one step is not present while another
plays; union them and one step's owner covers for every other step. That is how
a level of `Ciclo Energia` that never writes a strobe channel hides behind the
level beside it, which does (Codex review of `estrobo pegado`, 2026-08-28).

Enumerating the instants themselves is hopeless - a state built of a dozen
concurrent chasers has their step counts multiplied together - and unnecessary.
Two booleans per node answer it in one walk:

- **`lit_and_free`**: some instant of this node lights the fixture and leaves
  the channel unwritten. This is the latch.
- **`free`**: some instant of this node leaves the channel unwritten.

A **Chaser** picks one step, so both are `any` over its steps. A **Collection**
runs all its members at once, so an instant of it is one instant of each: the
channel is unwritten only if *every* member left it unwritten, and the fixture
is lit if *any* member lit it. Hence the collection latches when every member
has a `free` instant and at least one of those also lights the fixture - and a
single member that always writes the channel is enough to own it for the whole
collection, which is exactly the wiring the wash heads already have.

**This over-approximates, on purpose.** Treating each member's instants as
independently choosable assumes the concurrent chasers can be caught in every
combination of their steps. Over a night of drifting step lengths they very
nearly can, but two chasers locked to the same clock never would, so a latch
reported here is "reachable unless the timing forbids it" rather than "certain".
That is the right direction to err for a rule about a strobe nobody can stop:
the union it replaces erred the other way and stayed silent. A checker that
modelled the timing would need to model the show, which is the thing it exists
not to have to do.
"""

from .driven_channels import driven_channels
from .show_graph import ShowGraph, lit


def unowned_while_lit(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    function_id: int,
    fixture_id: int,
    offsets: frozenset[int],
    dimmers: tuple[int, ...],
) -> bool:
    """Whether some instant of this function lights the fixture with one of
    `offsets` left to whatever the last writer put there."""
    return any(
        _latch(graph, groups, function_id, fixture_id, offset, dimmers, set())[0]
        for offset in offsets
    )


def _latch(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    function_id: int,
    fixture_id: int,
    offset: int,
    dimmers: tuple[int, ...],
    seen: set[int],
) -> tuple[bool, bool]:
    """(lit_and_free, free) for one node and one channel."""
    function = graph.functions.get(function_id)
    if function is None or function_id in seen:
        return (False, True)

    members = graph.members.get(function_id, ())
    if not members:
        written = driven_channels(function, graph.capabilities, groups).get(
            fixture_id, {}
        )
        free = offset not in written
        lights = any(lit(written.get(d, 0)) for d in dimmers)
        return (free and lights, free)

    seen = seen | {function_id}
    parts = [
        _latch(graph, groups, member, fixture_id, offset, dimmers, seen)
        for member in members
    ]
    if function.attrib.get("Type") == "Collection":
        free = all(part[1] for part in parts)
        return (free and any(part[0] for part in parts), free)
    return (any(part[0] for part in parts), any(part[1] for part in parts))
