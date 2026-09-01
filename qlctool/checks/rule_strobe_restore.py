"""A flashed strobe that keeps firing after the finger leaves the button.

Strobe channels are LTP: the last value written stays until somebody writes
another. A Flash button writes its strobing value while held and takes only
its own fader away on release - QLC+ restores nothing, because nothing in it
remembers what was there before. If the state running underneath never drives
that strobe channel, the flash's value simply stays: the owner pressed
`FLASH` once and the four panels strobed until somebody found `Strobo OFF`
by hand (owner, 2026-08-28, "se queda el estrobo para siempre").

The wiring that survives this is the one the wash heads already have: every
scene that lights them also parks their shutter channel, so the instant the
flash releases, the running state writes the strobe back off. The rule demands
that shape everywhere: every strobe-capable channel a Flash scene strobes must
be driven by each room state that lights the fixture. A state that keeps the
fixture dark is excused - the latch is invisible until a lit state runs, and
that lit state is the one required to clear it.

A state is read one **instant** at a time (`unowned_while_lit`), not as the
union of everything it reaches. A chaser's steps are alternatives, so a level
that never writes the strobe channel is a latch of its own even when the level
beside it writes strobe-off; merging them would let one level cover for the
next (2026-08-28, from the Codex review of `estrobo pegado`).

Sibling of `rule_accent_restore`, which reads the same LTP latch off the wheel
channels; this one is an error, not a warning, because a strobe nobody can
stop in a dark room full of people is a hazard, not a parked gobo.
"""

from lxml import etree

from .. import roles
from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, iter_local
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph
from .strobe_written import strobe_capable_offsets, value_strobes
from .unowned_instant import unowned_while_lit

RULE = "estrobo pegado"


def check_strobe_restore(
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
        findings += _latched(
            graph,
            groups,
            function_id,
            scene,
            states,
            button.attrib.get("Caption", ""),
        )
    return findings


def _latched(
    graph: ShowGraph, groups, function_id: int, scene, states, caption: str
) -> list[Finding]:
    findings: list[Finding] = []
    for fixture_id, written in driven_channels(scene, graph.capabilities, groups).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None or capability.is_smoke:
            continue
        strobed = {
            offset
            for offset, strobing in strobe_capable_offsets(capability).items()
            if written.get(offset) is not None and value_strobes(strobing, written[offset])
        }
        if not strobed:
            continue
        dimmers = capability.offsets_for_role(roles.DIMMER)
        orphan_states = sorted(
            graph.name(state_id)
            for state_id in states
            if unowned_while_lit(
                graph,
                groups,
                state_id,
                fixture_id,
                frozenset(strobed),
                tuple(dimmers),
            )
        )
        if not orphan_states:
            continue
        findings.append(
            Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(function_id),
                message=(
                    f"el flash «{caption}» estroba un canal que "
                    f"{', '.join(orphan_states)} no escribe: al soltar, el canal "
                    f"LTP se queda estrobando hasta que alguien lo apague a mano"
                ),
                fixtures=(capability.fixture.name,),
            )
        )
    return findings
