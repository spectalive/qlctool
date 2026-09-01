"""The vertical fog column only ever fires while a finger is on the button.

The four vertical machines are not haze. They fire a column of fog a metre
wide, lit from inside, and they empty a tank doing it: "el humo vertical nunca
debe dispararse solo" (owner, 2026-08-30). The ambient machine is the opposite
and always has been - a haze that has to be *on a timer*, because a room with
no haze in it shows no beams at all.

So the two are separated by shape, not by name: a machine that carries lights
is a column and belongs to a **held** button; a fog-only machine is haze and
its timer is the show's business. What this rule forbids is the column's pump
appearing anywhere a latch can reach - inside AUTO, inside a level, under a
Toggle button - because every one of those keeps fogging with nobody in the
room.

A held button is a `Flash`, and QLC+ only flashes a Scene (`rule_flash_scene`),
so a column that passes this rule is a column that stops the frame after the
key comes up.
"""

from lxml import etree

from .. import roles
from ..fog_offsets import fog_offsets
from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, iter_local
from .finding import ERROR, Finding
from .show_graph import ShowGraph, lit, reach

RULE = "columna automatica"


def check_held_column(graph: ShowGraph, groups, root: etree._Element) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    columns = {
        fixture_id: capability
        for fixture_id, capability in graph.capabilities.items()
        if capability.is_smoke and capability.has_role(roles.RED)
    }
    if not columns:
        return []

    findings: list[Finding] = []
    for button in iter_local(console, "Button"):
        function = find_local(button, "Function")
        if function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if function_id not in graph.functions:
            continue
        action = find_local(button, "Action")
        if action is not None and (action.text or "").strip() == "Flash":
            continue
        driven = reach(graph, groups, function_id)
        fired = sorted(
            capability.fixture.name
            for fixture_id, capability in columns.items()
            if any(
                lit(driven.get(fixture_id, {}).get(offset, 0)) for offset in fog_offsets(capability)
            )
        )
        if fired:
            findings.append(
                Finding(
                    rule=RULE,
                    severity=ERROR,
                    function=graph.name(function_id),
                    message=(
                        "dispara la bomba de las columnas de humo desde un boton "
                        "que se queda enganchado: la columna solo debe salir "
                        "mientras se mantiene pulsada la tecla"
                    ),
                    fixtures=tuple(fired),
                )
            )
    return findings
