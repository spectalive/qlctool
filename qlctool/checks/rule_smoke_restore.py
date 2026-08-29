"""A flashed pump that keeps fogging after the finger leaves the button.

The pump is LTP like every other channel: a Flash writes its value while held
and restores nothing on release - QLC+ takes the flash's own fader away, and
the channel keeps the last value written unless something running underneath
writes another. `rule_strobe_restore` is the same latch on the strobe channels,
and it cost a night of panels flashing until somebody found `Strobo OFF`.

On a pump it costs the tank, and the room: "le doy y nunca se para, se supone
que solo debe tirar cuando le de" (owner, live, 2026-08-29, four vertical LED
fog machines). `Humo Vertical YA` raised the Fog channel and no room state ever
wrote it, so the first press fogged until the workspace was reloaded.

Every room state must therefore drive the pump a smoke flash raises - at zero,
which is the only value that means "not fogging". A state is not excused for
keeping the machine dark the way `rule_strobe_restore` excuses one: a pump does
not care whether anything is lit.
"""

from lxml import etree

from ..fog_offsets import fog_offsets
from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, iter_local
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph, lit, reach

RULE = "humo pegado"


def check_smoke_restore(
    graph: ShowGraph, groups, root: etree._Element, states: set[int]
) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None or not states:
        return []
    state_reach = {
        state_id: reach(graph, groups, state_id) for state_id in states
    }
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
        findings += _latched(
            graph, groups, function_id, scene, state_reach,
            button.attrib.get("Caption", ""),
        )
    return findings


def _latched(
    graph: ShowGraph, groups, function_id: int, scene, state_reach, caption: str
) -> list[Finding]:
    findings: list[Finding] = []
    for fixture_id, written in driven_channels(
        scene, graph.capabilities, groups
    ).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None or not capability.is_smoke:
            continue
        fired = {
            offset for offset in fog_offsets(capability)
            if offset in written and lit(written[offset])
        }
        if not fired:
            continue
        orphan_states = sorted(
            graph.name(state_id)
            for state_id, driven in state_reach.items()
            if fired - set(driven.get(fixture_id, {}))
        )
        if not orphan_states:
            continue
        findings.append(Finding(
            rule=RULE,
            severity=ERROR,
            function=graph.name(function_id),
            message=(
                f"el flash «{caption}» abre la bomba de humo en un canal que "
                f"{', '.join(orphan_states)} no escribe: al soltar, el canal "
                "LTP se queda abierto y la maquina tira hasta vaciar el "
                "deposito"
            ),
            fixtures=(capability.fixture.name,),
        ))
    return findings
