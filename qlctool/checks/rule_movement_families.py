"""One movement geometry stretched over two kinds of optics.

The rig's movers are two families that share nothing but pan and tilt: washes,
whose wide soft beam wants big slow curves, and the 7R beams, whose 2-degree
needle sweeps a wall of light through faces at the same width and speed. All
twelve ran the same 100x100 EFX for weeks - the Codex review of 2026-08-27
called it out: professional systems expose movement size and speed per fixture
family precisely because one preset cannot fit both.

The families are read off capability, not name: a mover with a gobo wheel is a
beam-class fixture, one without is a wash. An EFX that mixes them is a shape
tuned for neither, and whichever family it was sized for, the other one is
doing something nobody designed.
"""

from .. import roles
from ..xmlutil import find_local, findall_local
from .driven_channels import EFX_PAN_TILT
from .finding import WARNING, Finding
from .show_graph import ShowGraph

RULE = "familias de movimiento mezcladas"


def check_movement_families(graph: ShowGraph) -> list[Finding]:
    findings: list[Finding] = []
    for function_id in sorted(graph.functions):
        function = graph.functions[function_id]
        if function.attrib.get("Type") != "EFX":
            continue
        washes: list[str] = []
        beams: list[str] = []
        for element in findall_local(function, "Fixture"):
            identifier = find_local(element, "ID")
            if identifier is None or not (identifier.text or "").strip().isdigit():
                continue
            # Only participants the EFX moves: in Dimmer or RGB mode the same
            # element is an intensity wave, and a dimmer does not care what
            # optics it sits behind.
            mode = find_local(element, "Mode")
            mode_value = (
                int(mode.text) if mode is not None and mode.text else EFX_PAN_TILT
            )
            if mode_value != EFX_PAN_TILT:
                continue
            capability = graph.capabilities.get(int(identifier.text))
            if capability is None:
                continue
            side = beams if capability.has_role(roles.GOBO) else washes
            side.append(capability.fixture.name)
        if not washes or not beams:
            continue
        findings.append(Finding(
            rule=RULE,
            severity=WARNING,
            function=graph.name(function_id),
            message=(
                f"mueve {len(washes)} wash(es) y {len(beams)} beam(s) con la "
                f"misma geometria; un haz de 2 grados y un wash ancho no "
                f"comparten tamaño ni velocidad - un EFX por familia"
            ),
            fixtures=tuple(sorted(washes + beams)),
        ))
    return findings
