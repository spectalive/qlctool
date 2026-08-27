"""A strobe scene that strobes part of the rig and silently skips the rest.

`Strobo ON` shipped driving only the channels whose definitions carry a
labelled strobing range - ten fixtures flashing while the seven Vortex PARs
and the pixel panels, whose strobe channel is a bare speed with no labels,
held steady (found live, 2026-08-27). Nothing warned, because the scene it
did write was correct; what was wrong was who it never wrote.

The rule reads the shape, not the name: a scene whose writes all land on
strobe-role channels, at least one of them actually strobing, is a strobe
scene, and a strobe scene must write every patched, non-smoke fixture that
has a strobe-capable channel. The strobing write is what separates it from
`Intensidad Peak`, which opens two shutters as its intensity path and strobes
nothing. The reopening scene is not checked - it has the same shape as any
opener - but the generator builds it from the same fixture list as the ON,
so covering one covers the other.
"""

from .. import roles
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph
from .strobe_written import strobe_capable_offsets, value_strobes

RULE = "estrobo incompleto"


def check_strobe_coverage(graph: ShowGraph, groups) -> list[Finding]:
    capable = {
        fixture_id: offsets
        for fixture_id, capability in graph.capabilities.items()
        if not capability.is_smoke
        and (offsets := strobe_capable_offsets(capability))
    }
    findings: list[Finding] = []
    for function_id in sorted(graph.functions):
        function = graph.functions[function_id]
        if function.attrib.get("Type") != "Scene":
            continue
        written = driven_channels(function, graph.capabilities, groups)
        if not written or not _all_strobe_writes(graph, written):
            continue
        if not _any_strobing_write(graph, written):
            continue
        missing = [
            graph.capabilities[fixture_id].fixture.name or str(fixture_id)
            for fixture_id in sorted(capable)
            if fixture_id not in written
        ]
        if missing:
            findings.append(Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(function_id),
                fixtures=tuple(missing),
                message=(
                    f"es una escena de estrobo que deja fuera {len(missing)} "
                    f"aparatos con canal de estrobo: media sala parpadea y la "
                    f"otra media se queda mirando"
                ),
            ))
    return findings


def _all_strobe_writes(graph: ShowGraph, written) -> bool:
    """Every written channel is a strobe-role channel, on every fixture."""
    for fixture_id, pairs in written.items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            return False
        strobe_offsets = set(capability.offsets_for_role(roles.STROBE))
        if not set(pairs) <= strobe_offsets:
            return False
    return True


def _any_strobing_write(graph: ShowGraph, written) -> bool:
    """At least one written value actually strobes its channel."""
    for fixture_id, pairs in written.items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        capable = strobe_capable_offsets(capability)
        for offset, value in pairs.items():
            if value is None or offset not in capable:
                continue
            if value_strobes(capable[offset], value):
                return True
    return False
