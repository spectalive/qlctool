"""Two programmes writing the same channel at the same time.

The owner's own words for the bug: "estamos pisando los colores con otro
programa encima". It is the hardest kind to see by eye, because both functions
are correct on their own - the rig-wide colour wheel is right, the bars' matrix
is right, and running them over the same bar gives a colour neither of them
chose.

Simultaneity is read off the function types. A **Collection** starts every
member at once, so its members are concurrent with each other. A **Chaser**
plays its steps one at a time, so steps are alternatives and never collide -
which is exactly why the energy levels were safe inside `Ciclo Energia` and
dangerous as three buttons somebody could press together.

A member's *reach* - every channel it can drive through anything it starts, at
any step - is what gets compared. If two concurrent members reach the same
contested channel, then at some step of some chaser both are writing it, and
the room shows the sum.
"""

from itertools import combinations

from .color_roles import CONTESTED
from .finding import ERROR, Finding
from .show_graph import ShowGraph, reach

RULE = "colores pisados"


def check_collisions(graph: ShowGraph, groups, entries: dict[int, str]) -> list[Finding]:
    findings: list[Finding] = []
    reported: set[tuple[int, int, int]] = set()
    for function_id in sorted(entries):
        for collection_id in graph.collections(function_id):
            findings += _collection(graph, groups, collection_id, reported)
    return findings


def _collection(graph: ShowGraph, groups, collection_id: int, reported) -> list[Finding]:
    members = graph.members.get(collection_id, ())
    if len(members) < 2:
        return []
    contested = {
        member: _contested_channels(graph, groups, member) for member in members
    }
    findings: list[Finding] = []
    for first, second in combinations(members, 2):
        shared = contested[first].keys() & contested[second].keys()
        if not shared:
            continue
        key = (collection_id, first, second)
        if key in reported:
            continue
        reported.add(key)
        fixtures = sorted({
            graph.capabilities[fixture_id].fixture.name
            for fixture_id, _ in shared
            if fixture_id in graph.capabilities
        })
        findings.append(Finding(
            rule=RULE,
            severity=ERROR,
            function=graph.name(collection_id),
            message=(
                f"arranca a la vez «{graph.name(first)}» y «{graph.name(second)}», "
                f"y los dos escriben los mismos canales de color, rueda o "
                f"posicion: se suman en vez de elegir"
            ),
            fixtures=tuple(fixtures),
        ))
    return findings


def _contested_channels(graph: ShowGraph, groups, function_id: int) -> dict:
    """(fixture, offset) this function can drive, restricted to what may fight."""
    driven = reach(graph, groups, function_id)
    contested = {}
    for fixture_id, written in driven.items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        wanted = {
            offset
            for role in CONTESTED
            for offset in capability.offsets_for_role(role)
        }
        for offset, value in written.items():
            # A channel driven to zero everywhere is a fixture being turned
            # off, not a second opinion about its colour.
            if offset in wanted and (value is None or value > 0):
                contested[(fixture_id, offset)] = value
    return contested
