"""A colour stated on a fixture with a white emitter, and the emitter left out.

The two Mini Led heads carry a White channel beside their RGB, and each of the
MAC WASH's three rings has one. No look in the show had ever written any of
them: `Blanco Total`, both flashes, `Rig Blanco` and `Luz Charla` mixed their
white out of red, green and blue at 255 and left the white LED - the brightest
and truest white the fixture has - at 0 (Codex, cross-audit 2026-09-02). The
generator only ever spoke red, green and blue.

The rule: a Scene that writes red, green or blue on a fixture writes that
fixture's white channels too, at whatever value the colour calls for (zero for
a saturated one - `white_level`). A matrix cannot, and is not asked to: it
paints RGB by design.
"""

from .. import roles
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE = "blanco sin emisor blanco"
RGB = (roles.RED, roles.GREEN, roles.BLUE)


def check_white_emitter(graph: ShowGraph, groups) -> list[Finding]:
    findings: list[Finding] = []
    for function_id, function in sorted(graph.functions.items()):
        if function.attrib.get("Type") != "Scene":
            continue
        skipped: list[str] = []
        for fixture_id, written in driven_channels(function, graph.capabilities, groups).items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None:
                continue
            whites = capability.offsets_for_role(roles.WHITE)
            if not whites:
                continue
            states_rgb = any(
                offset in written for role in RGB for offset in capability.offsets_for_role(role)
            )
            if states_rgb and any(offset not in written for offset in whites):
                skipped.append(capability.fixture.name)
        if not skipped:
            continue
        findings.append(
            Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(function_id),
                fixtures=tuple(sorted(set(skipped))),
                message=(
                    f"escribe rojo, verde y azul en {len(set(skipped))} aparatos "
                    f"con emisor White y no escribe ese canal: el blanco sale "
                    f"mezclado de tres LED y el cuarto, el mas brillante, se queda "
                    f"a cero"
                ),
            )
        )
    return findings
