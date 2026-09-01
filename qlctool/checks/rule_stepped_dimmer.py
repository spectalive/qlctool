"""A fraction sent to a dimmer that has no fractions - the crescent beam.

2026-08-29, live, the owner reading the desk: "las 7R no se abren del todo,
están como una media luna ... el canal 7 de cada 7R está a la mitad en vez de
abierto del todo". Channel 7 is the BEAM 230W 7R's dimmer, and on a 7R that is
a mechanical blade crossing the aperture, not a fader. At 110 - the value
`Intensidad Ambiente` wrote to every dimmer in the rig, and held for the quiet
level's four minutes - the blade sits half across the lens and the beam comes
out as a crescent.

The rule reads the definition, not the model: a dimmer channel described in
**labelled ranges** is one whose author had to describe it in steps, and a
channel described in steps has no fraction to give (`stepped_dimmer`). A plain
fader declares no ranges at all, so nothing else in this rig is asked about.

An EFX in Dimmer mode over such a channel is the same fault in motion - it
sweeps the blade, so most of every pass is a half-moon - and is caught here
too, since the value it writes is unknowable rather than an end.
"""

from ..stepped_dimmer import stepped_dimmer_offsets
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE = "dimmer a medias"
WRITES_VALUES = ("Scene", "Sequence", "EFX")


def check_stepped_dimmer(graph: ShowGraph, groups) -> list[Finding]:
    findings: list[Finding] = []
    for function_id in sorted(graph.functions):
        function = graph.functions[function_id]
        if function.attrib.get("Type") not in WRITES_VALUES:
            continue
        caught: set[str] = set()
        driven = driven_channels(function, graph.capabilities, groups)
        for fixture_id, written in driven.items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None:
                continue
            for offset in stepped_dimmer_offsets(capability):
                if offset not in written:
                    continue
                if _is_a_step(capability, offset, written[offset]):
                    continue
                caught.add(capability.fixture.name)
        if caught:
            findings.append(
                Finding(
                    rule=RULE,
                    severity=ERROR,
                    function=graph.name(function_id),
                    message=(
                        "escribe un valor intermedio en un dimmer que no es un "
                        "fader sino una pala mecanica: a medio recorrido tapa "
                        "media lente y el haz sale como una media luna - o abierto "
                        "del todo o cerrado"
                    ),
                    fixtures=tuple(sorted(caught)),
                )
            )
    return findings


def _is_a_step(capability, offset: int, value: int | None) -> bool:
    """Whether this value lands on one of the channel's own end positions.

    None - an EFX driving the channel to a value nobody can predict - is never
    a step: a swept blade is a crescent for most of its travel.
    """
    if value is None:
        return False
    ranges = capability.capabilities_by_offset[offset]
    ends = (min(r.minimum for r in ranges), max(r.maximum for r in ranges))
    return value in ends
