"""A room state that lights a fixture and inherits its wheels from the last one.

The solo frame stops the running state and starts the next; that is all it
does. Every LTP channel keeps what the old state left there, because QLC+
zeroes only the Intensity group each cycle. So a state that opens a fixture
without writing its gobo, prism, prism rotation, shake, focus, zoom, colour
wheel or position shows *the previous state's* choice of all of them: `Todo
Negro` -> `Blanco Total` after a party level was four white beams projecting
Gobo 5 through an inserted, spinning prism, wherever the figure had left them
(cross-audit, 2026-09-02). `Momento Charla` never had the problem because it
parks all of it beside its light.

The rule: for every fixture a state lights, every one of those channels that
*some other state* can leave at a value that shows (anything but 0) must be
written by this state too. A state that keeps the fixture dark is excused - a
prism nobody can see through a shut dimmer is nobody's business until the
next state, whose business it then is.
"""

from .. import roles
from .finding import ERROR, Finding
from .fixture_lit_in_state import fixture_lit_in_state
from .left_showing import left_showing
from .reach import reach
from .show_graph import ShowGraph

RULE_ID = "state_handover"
INHERITED_ROLES = (
    roles.COLOR_MACRO,
    roles.GOBO,
    roles.GOBO_SHAKE,
    roles.PRISM,
    roles.PRISM_ROTATION,
    roles.FOCUS,
    roles.ZOOM,
    roles.PAN,
    roles.TILT,
)


def check_state_handover(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], states: set[int]
) -> list[Finding]:
    if len(states) < 2:
        return []
    reaches = {state_id: reach(graph, groups, state_id) for state_id in states}
    findings: list[Finding] = []
    for state_id in sorted(states):
        inherited: dict[str, set[str]] = {}
        for fixture_id, written in reaches[state_id].items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None or not fixture_lit_in_state(capability, written):
                continue
            for role in INHERITED_ROLES:
                for offset in capability.offsets_for_role(role):
                    if offset in written:
                        continue
                    if not left_showing(reaches, state_id, fixture_id, offset):
                        continue
                    inherited.setdefault(role, set()).add(capability.fixture.name)
        if not inherited:
            continue
        roles_named = ", ".join(sorted(inherited))
        fixtures = sorted({name for names in inherited.values() for name in names})
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=ERROR,
                function=graph.name(state_id),
                fixtures=tuple(fixtures),
                message_id="state_handover_inherits",
                fields={"count": len(fixtures), "roles": roles_named},
            )
        )
    return findings
