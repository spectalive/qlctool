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

A static floor is the exception (`static_floors`): a Scene a room state
starts before every member that writes its channels, on LTP channels only, is
overridden by each of them while they run and holds the channel when they
stop. That order is QLC+ 5's, measured, so the pair is a floor under a look,
not two looks fighting.
"""

from collections.abc import Collection

from .contested_collection_members import contested_collection_members
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE_ID = "collision"


def check_collisions(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    entries: dict[int, str],
    states: Collection[int],
) -> list[Finding]:
    findings: list[Finding] = []
    reported: set[tuple[int, int, int]] = set()
    for function_id in sorted(entries):
        for collection_id in graph.collections(function_id):
            for first, second, fixtures in contested_collection_members(
                graph, groups, collection_id, reported, states
            ):
                findings.append(
                    Finding(
                        rule_id=RULE_ID,
                        severity=ERROR,
                        function=graph.name(collection_id),
                        message_id="collision_same_channels",
                        fields={"first": graph.name(first), "second": graph.name(second)},
                        fixtures=fixtures,
                    )
                )
    return findings
