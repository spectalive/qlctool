"""A fog machine's own light must be programmed, or the column fires dark.

The vertical fog machines carry LEDs meant to light the column, and DMX
priority: with the controller plugged in, the machine's internal colour
program is dead (scanned manual + Audibax Geyser 2000 RGB manual, 2026-08-29).
So a show that fires the pump and never writes the dimmer-plus-colour has not
half-programmed the machine - it has switched its light off for the night.

The rule reasons about capabilities: any smoke-typed fixture that has colour
channels and whose pump some function fires must also have some function that
puts its LED dimmer and at least one colour up together - the machine only
shows light when both are.
"""

from .. import roles
from ..fog_offsets import fog_offsets
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph, lit

RULE = "humo-luz"


def check_smoke_light(graph: ShowGraph, groups, entries) -> list[Finding]:
    findings: list[Finding] = []
    for fixture_id, capability in sorted(graph.capabilities.items()):
        if not capability.is_smoke or not capability.has_role(roles.RED):
            continue
        pump = set(fog_offsets(capability))
        dimmer = set(capability.offsets_for_role(roles.DIMMER))
        colours = {
            offset
            for role in (roles.RED, roles.GREEN, roles.BLUE)
            for offset in capability.offsets_for_role(role)
        }
        fired = False
        lit_somewhere = False
        for function in graph.functions.values():
            written = driven_channels(
                function, graph.capabilities, groups
            ).get(fixture_id)
            if not written:
                continue
            if any(lit(v) for o, v in written.items() if o in pump):
                fired = True
            if any(lit(v) for o, v in written.items() if o in dimmer) and any(
                lit(v) for o, v in written.items() if o in colours
            ):
                lit_somewhere = True
        if fired and not lit_somewhere:
            findings.append(Finding(
                rule=RULE,
                severity=ERROR,
                function="",
                message=(
                    "la maquina de humo con luz dispara la columna pero "
                    "ninguna funcion enciende su LED (dimmer + color a la "
                    "vez): con DMX conectado su programa interno queda "
                    "anulado y la columna sale a oscuras"
                ),
                fixtures=(capability.fixture.name,),
            ))
    return findings
