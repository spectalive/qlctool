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
from .color_roles import COLOUR
from .finding import ERROR, Finding
from .show_graph import ShowGraph, lit, reach

RULE = "estado que hereda"
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


def check_state_handover(graph: ShowGraph, groups, states: set[int]) -> list[Finding]:
    if len(states) < 2:
        return []
    reaches = {state_id: reach(graph, groups, state_id) for state_id in states}
    findings: list[Finding] = []
    for state_id in sorted(states):
        inherited: dict[str, set[str]] = {}
        for fixture_id, written in reaches[state_id].items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None or not _lights(capability, written):
                continue
            for role in INHERITED_ROLES:
                for offset in capability.offsets_for_role(role):
                    if offset in written:
                        continue
                    if not _left_showing(reaches, state_id, fixture_id, offset):
                        continue
                    inherited.setdefault(role, set()).add(capability.fixture.name)
        if not inherited:
            continue
        roles_named = ", ".join(sorted(inherited))
        fixtures = sorted({name for names in inherited.values() for name in names})
        findings.append(
            Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(state_id),
                fixtures=tuple(fixtures),
                message=(
                    f"enciende {len(fixtures)} aparatos sin escribir {roles_named}: "
                    f"esos canales son LTP y se quedan como los dejo el estado "
                    f"anterior - la luz de trabajo sale con el gobo y el prisma "
                    f"del ultimo nivel"
                ),
            )
        )
    return findings


def _lights(capability, written: dict[int, int | None]) -> bool:
    dimmers = capability.offsets_for_role(roles.DIMMER)
    if dimmers:
        return any(lit(written.get(offset, 0)) for offset in dimmers)
    coloured = {offset for role in COLOUR for offset in capability.offsets_for_role(role)}
    return any(lit(written[offset]) for offset in coloured if offset in written)


def _left_showing(reaches, state_id: int, fixture_id: int, offset: int) -> bool:
    """Whether another state can leave this channel at a value that is not 0."""
    for other_id, other in reaches.items():
        if other_id == state_id:
            continue
        value = other.get(fixture_id, {}).get(offset)
        if value is None and offset in other.get(fixture_id, {}):
            return True
        if value:
            return True
    return False
