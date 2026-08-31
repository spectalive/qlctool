"""A held accent on a wheel channel that nothing puts back afterwards.

Gobo, prism and colour-wheel channels are LTP: the last value written stays
until somebody writes another. A Flash button is a *temporary* writer - press,
accent, release - but release only takes the flash's own writes away; it does
not restore what was there before, because nothing in QLC+ remembers that. If
the state running underneath never drives that wheel, the accent's position
simply stays: the prism that was flashed for one drop is still in the beam an
hour later, and nobody can say which button did it (Codex review, 2026-08-27).

So every wheel channel a Flash scene touches needs an owner underneath: each
room state that lights the fixture must itself drive that channel, so the
moment the flash releases, the state writes the wheel back where it belongs. A
state that keeps the fixture dark is excused - a wheel nobody can see through
a closed dimmer restores nothing but also shows nothing.
"""

from lxml import etree

from .. import roles
from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, iter_local
from .driven_channels import driven_channels
from .finding import WARNING, Finding
from .show_graph import ShowGraph
from .unowned_instant import unowned_while_lit

RULE = "acento sin dueño"
WHEEL_ROLES = (roles.COLOR_MACRO, roles.GOBO, roles.PRISM)


def check_accent_restore(
    graph: ShowGraph, groups, root: etree._Element, states: set[int]
) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None or not states:
        return []
    findings: list[Finding] = []
    for button in iter_local(console, "Button"):
        action = find_local(button, "Action")
        if action is None or (action.text or "").strip() != "Flash":
            continue
        function = find_local(button, "Function")
        if function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        scene = graph.functions.get(function_id)
        if scene is None:
            continue
        findings += _orphaned(
            graph, groups, function_id, scene, states,
            button.attrib.get("Caption", ""),
        )
    return findings


def _orphaned(
    graph: ShowGraph, groups, function_id: int, scene, states, caption: str
) -> list[Finding]:
    findings: list[Finding] = []
    for fixture_id, written in driven_channels(
        scene, graph.capabilities, {}
    ).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        wheels = {
            offset
            for role in WHEEL_ROLES
            for offset in capability.offsets_for_role(role)
        }
        touched = wheels & set(written)
        if not touched:
            continue
        dimmers = capability.offsets_for_role(roles.DIMMER)
        orphan_states = sorted(
            graph.name(state_id)
            for state_id in states
            if unowned_while_lit(
                graph, groups, state_id, fixture_id,
                frozenset(touched), tuple(dimmers),
            )
        )
        if not orphan_states:
            continue
        findings.append(Finding(
            rule=RULE,
            severity=WARNING,
            function=graph.name(function_id),
            message=(
                f"el flash «{caption}» mueve una rueda (gobo, prisma o "
                f"color) que {', '.join(orphan_states)} no escribe: al soltar, "
                f"la rueda se queda donde el flash la dejo y nadie la devuelve"
            ),
            fixtures=(capability.fixture.name,),
        ))
    return findings
