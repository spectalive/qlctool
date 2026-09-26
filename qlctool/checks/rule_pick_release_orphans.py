"""A latched pick that, released, leaves part of its family with no owner.

Picks stay latched (ruling D8): a Toggle in a family SoloFrame, which stops
the frame's hook when it starts. Toggled off, QLC+ 5 stops the pick and
restarts nothing (`vcbutton.cpp`; `vcsoloframe.cpp` has no restore), so the
instant after a release is the room state with every function of the frame
stopped (`released_reach`). The HTP channels of the family go dark with it,
which is clean. The LTP ones keep whatever the pick wrote (`latched_on_lit`):
on 2026-09-26 releasing `Rig Rojo` left the rig black and the four 7R red,
because their wheel is LTP and their blade was held open by the level; Gobo
Shake kept shaking under FIESTA; a released figure left the heads at 127
(en-sala DMX audit, item 5 and concern C3).

The tablet presses the frame's hook on a release (`releaseTo` in the desk
map); the pad and the keyboard do not, so the generator owes a release that
leaves nothing half-owned: a lit, rigged fixture holding an LTP channel of the
pick's family that nothing the state still runs writes is reported - an error
for a colour, since that is a beam in one colour over a rig in none, and a
warning for a wheel or a position. Graph, roles and channel groups only.
"""

from lxml import etree

from .. import roles
from ..rigged_fixture_ids import rigged_fixture_ids
from ..xmlutil import find_local, iter_local
from .family_frames import FAMILIES, family_frame_handoff
from .finding import ERROR, WARNING, Finding
from .latched_on_lit import latched_on_lit
from .released_reach import released_reach
from .show_graph import ShowGraph

RULE_ID = "pick_release_orphans"


def check_pick_release_orphans(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], root: etree._Element, states: set[int]
) -> list[Finding]:
    """One finding per pick whose release leaves a lit fixture holding its family."""
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    rigged = rigged_fixture_ids(root)
    findings: list[Finding] = []
    for frame in iter_local(console, "SoloFrame"):
        handoff = family_frame_handoff(graph, groups, states, frame)
        if handoff is None:
            continue
        _, toggles, hooks, families, _ = handoff
        family_roles = {role for family in families for role in FAMILIES.get(family, ())}
        if not family_roles:
            continue
        stopped = frozenset(toggles)
        released = {
            state_id: released_reach(graph, groups, state_id, stopped)
            for state_id in sorted(states)
            if graph.descendants(state_id) & hooks
        }
        # The colour family is the one a wheel colour belongs to.
        colour = roles.COLOR_MACRO in family_roles
        for pick_id in sorted(set(toggles) - hooks):
            fixtures: set[str] = set()
            left_in: list[str] = []
            for state_id, still in released.items():
                latched = latched_on_lit(graph, groups, pick_id, family_roles, rigged, still)
                if latched:
                    left_in.append(graph.name(state_id))
                    fixtures |= {graph.capabilities[f].fixture.name for f in latched}
            if fixtures:
                findings.append(
                    Finding(
                        rule_id=RULE_ID,
                        severity=ERROR if colour else WARNING,
                        function=graph.name(pick_id),
                        fixtures=tuple(sorted(fixtures)),
                        message_id=(
                            "pick_release_orphans_colour"
                            if colour
                            else "pick_release_orphans_latched"
                        ),
                        fields={"count": len(fixtures), "states": ", ".join(left_in)},
                    )
                )
    return findings
