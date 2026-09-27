"""A block of the automatic show that moves one family and parks the other.

2026-08-29, live: "las 7R ... no se mueven", with nothing pressed but AUTO.
Nothing was broken in the beams. `Nivel Ambiente` - the first and longest step
of `Ciclo Energia` - started the washes' slow shapes and a *static* fan scene
for the beams, so for the level's whole four-minute hold the four 7R held one
position. A needle that never moves does not read as rest; it reads as four
lights that failed.

The rule is about blocks the show runs by itself. A Collection that is a step
of a Chaser is such a block: it starts everything in it at once and holds for
that step. If anything in it moves a head, the block is a movement block, and
every head in the rig has to be moving inside it - a head left out is left out
for the whole step, however long that is.

A Collection somebody presses is not asked the same question: a button named
after one shape is allowed to move only the fixtures that draw that shape, and
the operator can see what they pressed.

Nor is a Collection made of nothing but EFX. That is one movement QLC+ made
us write twice: an EFX turns 16-bit handling off for every fixture in it when
one of them has a fine channel that is not directly after its coarse one, so a
family that mixes the two kinds is generated as two EFX under one Collection
(`keeps_16bit`). Since 2026-09-02 the Mini Led Moving Head declares its fine
channels at 14 and 15, and every wash figure became such a pair. A pair like
that as a step of the washes' own chaser is the same step it was as one EFX,
and the beams it does not move are moved by the beams' chaser beside it - the
block the rule is about is the one that mixes a scene into the step.
"""

from .. import roles
from .finding import ERROR, Finding
from .only_efx import only_efx
from .pan_tilt_block_fixtures import pan_tilt_block_fixtures
from .show_graph import CONCURRENT, ShowGraph

RULE_ID = "parked_movers"


def check_parked_movers(graph: ShowGraph) -> list[Finding]:
    movers = {
        fixture_id
        for fixture_id, capability in graph.capabilities.items()
        if not capability.is_smoke
        and capability.has_role(roles.PAN)
        and capability.has_role(roles.TILT)
    }
    if len(movers) < 2:
        return []

    findings: list[Finding] = []
    seen: set[int] = set()
    for chaser_id in sorted(graph.functions):
        if graph.kind(chaser_id) != "Chaser":
            continue
        for step in graph.members.get(chaser_id, ()):
            if graph.kind(step) != CONCURRENT or step in seen:
                continue
            seen.add(step)
            if only_efx(graph, step):
                continue
            moved = pan_tilt_block_fixtures(graph, step)
            if not moved:
                continue
            parked = movers - moved
            if not parked:
                continue
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(step),
                    message_id="parked_movers_still",
                    fixtures=tuple(
                        sorted(graph.capabilities[fixture_id].fixture.name for fixture_id in parked)
                    ),
                )
            )
    return findings
