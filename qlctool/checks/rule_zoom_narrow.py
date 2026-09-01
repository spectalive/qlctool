"""A wash lit by a scene that never states its zoom.

Until 2026-08-29 nothing in this rig had a zoom channel, so no generator had a
reason to mention one. That night two Mac Mah MAC WASH 1915Z came in place of
the CromoWash100s, and their beam width is DMX: a scene that sets colour and
dimmer and says nothing about zoom leaves the head wherever the last look left
it, which on a cold desk is 0 - six degrees, a coin on the back wall from a
fixture the plot calls a wash.

It is the shutter's lesson in a second channel: an unwritten channel is not a
neutral one, and the look that owns the light owns every channel that decides
whether the light is the shape it is meant to be.

The rule: a Scene that lights a fixture - dimmer or colour above zero - must
write that fixture's zoom too, when the definition gives it one that says which
end is wide (`zoom_wide_pairs`). Scenes that only move, only strobe or only
black out are not lighting anything and are left alone.
"""

from .. import roles
from ..zoom_wide import zoom_wide_pairs
from .driven_channels import driven_channels
from .finding import WARNING, Finding
from .show_graph import ShowGraph, lit

RULE = "zoom sin declarar"

LIGHTING_ROLES = (roles.DIMMER, roles.RED, roles.GREEN, roles.BLUE, roles.WHITE)


def check_zoom_narrow(graph: ShowGraph, groups) -> list[Finding]:
    findings: list[Finding] = []
    for function_id in sorted(graph.functions):
        if graph.kind(function_id) != "Scene":
            continue
        silent = _lit_without_zoom(graph, groups, function_id)
        if not silent:
            continue
        findings.append(
            Finding(
                rule=RULE,
                severity=WARNING,
                function=graph.name(function_id),
                message=(
                    "enciende la cabeza pero no escribe su zoom: se queda con el "
                    "que dejo el ultimo look, y sin nadie que lo escriba eso es 0 - "
                    "el haz mas cerrado que tiene"
                ),
                fixtures=tuple(sorted(silent)),
            )
        )
    return findings


def _lit_without_zoom(graph: ShowGraph, groups, function_id: int) -> list[str]:
    driven = driven_channels(graph.functions[function_id], graph.capabilities, groups)
    names: list[str] = []
    for fixture_id, written in driven.items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        zoom = zoom_wide_pairs(capability)
        if not zoom:
            continue
        if all(offset in written for offset, _ in zoom):
            continue
        if _lights(capability, written):
            names.append(capability.fixture.name)
    return names


def _lights(capability, written: dict[int, int | None]) -> bool:
    for role in LIGHTING_ROLES:
        for offset in capability.offsets_for_role(role):
            if offset in written and lit(written[offset]):
                return True
    return False
