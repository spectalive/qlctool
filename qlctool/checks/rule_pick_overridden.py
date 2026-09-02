"""A latched pick on a wheel or an aim that the state's own chaser steps over.

A gobo picked on the manual page, a prism put in, a colour on the beams'
wheel, the heads aimed at the stage: each is a Toggle scene writing an LTP
channel. Under a state whose chaser also steps that channel - `Gobo
Animacion` every 4 s, the prism dance every 8 s, the wash figures every 15 s,
the colour wheel every 3.3 s - the pick holds exactly until the next step.
QLC+ starts the step as a new function, the new function requests a new
fader, and `Universe::requestFader` appends it after every fader of its
priority, so the later write wins the LTP channel (cross-audit, 2026-09-02).
"Escenario" aimed the heads at the speaker for fifteen seconds.

The fix is priority, not order: a Flash button with `Override` gets the
Flashing priority, whose faders sit after every Auto fader however late those
start, so the pick holds for as long as the finger does. The rule therefore
reads Toggle scenes only, and only the channels that are picks - wheels,
their companions, and position - because those are the ones a person sets by
hand while the state runs.
"""

from lxml import etree

from .. import roles
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .layer_buttons import layer_buttons
from .show_graph import ShowGraph
from .stepped_leaves import stepped_leaves

RULE = "capa pisada por el ciclo"
PICK_ROLES = (
    roles.COLOR_MACRO,
    roles.GOBO,
    roles.GOBO_SHAKE,
    roles.PRISM,
    roles.PRISM_ROTATION,
    roles.FOCUS,
    roles.PAN,
    roles.PAN_FINE,
    roles.TILT,
    roles.TILT_FINE,
)


def check_pick_overridden(
    graph: ShowGraph, groups, root: etree._Element, states: set[int]
) -> list[Finding]:
    if not states:
        return []
    stepped = _stepped_writes(graph, groups, states)
    findings: list[Finding] = []
    for button in layer_buttons(root, states):
        scene = graph.functions.get(button.function_id)
        if scene is None or scene.attrib.get("Type") != "Scene":
            continue
        overridden: dict[str, set[str]] = {}
        for fixture_id, written in driven_channels(scene, graph.capabilities, groups).items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None:
                continue
            for offset in written:
                role = capability.roles_by_offset[offset]
                if role not in PICK_ROLES:
                    continue
                for state_id in stepped.get((fixture_id, offset), ()):
                    overridden.setdefault(graph.name(state_id), set()).add(
                        capability.fixture.name
                    )
        if not overridden:
            continue
        fixtures = sorted({name for names in overridden.values() for name in names})
        findings.append(
            Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(button.function_id),
                fixtures=tuple(fixtures),
                message=(
                    f"es un Toggle («{button.caption}») sobre una rueda o una "
                    f"posicion que un chaser de {', '.join(sorted(overridden))} "
                    f"vuelve a escribir en su siguiente paso: el fader nuevo "
                    f"entra detras y gana - la eleccion dura un paso; un Flash "
                    f"con Override dura lo que dure la mano"
                ),
            )
        )
    return findings


def _stepped_writes(graph: ShowGraph, groups, states: set[int]) -> dict[tuple[int, int], set[int]]:
    """(fixture, offset) -> the states whose chasers re-write it at a step."""
    found: dict[tuple[int, int], set[int]] = {}
    for state_id in states:
        for leaf_id in stepped_leaves(graph, state_id):
            leaf = graph.functions.get(leaf_id)
            if leaf is None:
                continue
            for fixture_id, written in driven_channels(leaf, graph.capabilities, groups).items():
                for offset in written:
                    found.setdefault((fixture_id, offset), set()).add(state_id)
    return found
