"""A rigged moving head that nothing aims, so it sits at mid-travel.

2026-09-26, en-sala DMX audit (items 2, 15 and 16, concern C4): the two MAC
WASH, the only rigged washes, sat at 127/127 through `Beams Abanico`,
`Beams Cruce`, `Escenario` and `Cabezas Centro`, and for the first 10 and
11.6 s of `Ola Vertical`. The picks stop the frame's movement hooks and wrote
the beams alone; `Escenario` aimed the addresses of two spare CromoWash; the
home scene parked the washes at mid-travel; and the wave was Serial over eight
washes, six of them spares, so the MACs waited for slots 7 and 8 with nothing
writing them. 127 is outside the washes' measured window: the wall behind the
stage.

The question is asked of every instant the console can make: each room state
that places the heads, and each pick of a position frame over each state, with
the frame's hooks stopped. Every rigged head must have a writer that aims it
(`aims_head`): a Scene value that is not mid-travel outside the window, or an
EFX that moves it from the start. The instant after a pick is released is not
asked yet - releasing a latched pick leaves its family with no owner at all,
which is the next cause in the plan (C8).
"""

from lxml import etree

from .. import roles
from ..rigged_fixture_ids import rigged_fixture_ids
from ..xmlutil import find_local, iter_local
from .finding import ERROR, Finding
from .position_frame_picks import position_frame_picks
from .show_graph import ShowGraph, reach
from .unaimed_evaluator import UnaimedEvaluator

RULE_ID = "unaimed_rigged_mover"


def check_unaimed_rigged_mover(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], root: etree._Element, states: set[int]
) -> list[Finding]:
    """One finding per state or position pick that can leave a rigged head unaimed."""
    rigged = rigged_fixture_ids(root)
    movers = {
        fixture_id: capability
        for fixture_id, capability in sorted(graph.capabilities.items())
        if fixture_id in rigged
        and not capability.is_smoke
        and capability.has_role(roles.PAN)
        and capability.has_role(roles.TILT)
    }
    if not movers:
        return []
    evaluator = UnaimedEvaluator(graph, groups)
    findings: list[Finding] = []
    for state_id in sorted(states):
        driven = reach(graph, groups, state_id)
        if not any(
            offset in driven.get(fixture_id, {})
            for fixture_id, capability in movers.items()
            for offset in capability.offsets_for_role(roles.PAN)
        ):
            continue
        left = [m for m in movers if evaluator.can_leave((state_id,), m, frozenset())]
        if left:
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(state_id),
                    message_id="unaimed_rigged_mover_state",
                    fields={"count": len(left)},
                    fixtures=tuple(sorted(movers[m].fixture.name for m in left)),
                )
            )
    console = find_local(root, "VirtualConsole")
    for frame in iter_local(console, "SoloFrame") if console is not None else ():
        for pick_id, stopped in position_frame_picks(graph, groups, states, frame):
            hits = [
                {m for m in movers if evaluator.can_leave((state_id, pick_id), m, stopped)}
                for state_id in sorted(states)
            ]
            left = sorted(set().union(*hits))
            if left:
                findings.append(
                    Finding(
                        rule_id=RULE_ID,
                        severity=ERROR,
                        function=graph.name(pick_id),
                        message_id="unaimed_rigged_mover_pick",
                        fields={"count": len(left), "states": sum(1 for hit in hits if hit)},
                        fixtures=tuple(sorted(movers[m].fixture.name for m in left)),
                    )
                )
    return findings
