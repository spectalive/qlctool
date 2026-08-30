"""A channel that hands the fixture back to itself, and nobody writing it.

`rule_internal_program` covers the fixtures whose own programmes are named -
a mode channel with a "no function" range and an "auto" one. This one covers
the rest, and the rest is most of them: the MAC WASH 1915Z's blanket `Function
Mode`, the MiN Wash's `Movement Macros`, the CLB2.4's `Preprogrammed automatic
Shows`, the vertical fog machines' `Colour Change`. One channel each, no names
to reason about, and the same consequence when it is up - the fixture stops
listening to the position, the colour or the dimmer the show is sending and
runs whatever it feels like.

The rule is about ownership, not about a value. A channel no function in the
whole show ever writes is a channel whose value is last night's, the previous
controller's, or a menu's. It cost the owner a night with the two new washes
on 2026-08-29: aimed at the measured audience window, coloured by a wheel that
steps every eight beats, and what the room saw was "cabezas mirando para abajo
y cambios de colores muy rapidos" - the fixture's own show, not this one.

So: any fixture some function lights, carrying a self-running channel that
nothing writes anywhere, is a finding. Writing zero is the show saying "obey
DMX" out loud; the fixture's own menu (RunMode DMX / AUTO / SOUND on the MAC
WASH) is beyond any file's reach and stays a job for the display on its back.
"""

from .. import roles
from ..internal_program import internal_program
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph, lit

RULE = "modo sin dueño"


def check_mode_owner(graph: ShowGraph, groups, entries) -> list[Finding]:
    del entries
    written: dict[int, set[int]] = {}
    lighted: set[int] = set()
    for function in graph.functions.values():
        for fixture_id, values in driven_channels(
            function, graph.capabilities, groups
        ).items():
            written.setdefault(fixture_id, set()).update(values)
            capability = graph.capabilities.get(fixture_id)
            if capability is None:
                continue
            if any(
                lit(values.get(offset, 0))
                for offset in capability.offsets_for_role(roles.DIMMER)
            ):
                lighted.add(fixture_id)

    findings: list[Finding] = []
    for fixture_id, capability in sorted(graph.capabilities.items()):
        if fixture_id not in lighted:
            continue
        if internal_program(capability) is not None:
            continue
        orphans = [
            offset
            for offset in capability.offsets_for_role(roles.EFFECT)
            if offset not in written.get(fixture_id, set())
        ]
        if orphans:
            findings.append(Finding(
                rule=RULE,
                severity=ERROR,
                function="",
                message=(
                    "el canal con el que el fixture corre sus propios "
                    "programas no lo escribe ninguna funcion del show: se "
                    "queda con lo que dejo la noche anterior y mientras este "
                    "arriba el aparato ignora posicion, color e intensidad"
                ),
                fixtures=(capability.fixture.name,),
            ))
    return findings
