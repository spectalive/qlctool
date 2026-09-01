"""A smoke button whose pump does not fall back to zero on its own.

QLC+ rebuilds its universe from the running faders every cycle, but it only
*resets* the channels in the **Intensity** group before doing so
(`Universe::processFaders` -> `zeroIntensityChannels`, engine/src/universe.cpp).
Every other group keeps whatever was last written. So a Flash over a channel
outside that group is not momentary at all: the release removes the flash's own
fader and the value simply stays.

That is what the four vertical fog machines did. Their Fog channel was declared
in the Effect group, `Humo Vertical YA` raised it while held, and letting go
changed nothing: "le doy y no para de echar todo el rato ... se supone que solo
debe tirar cuando le de" (owner, live, 2026-08-29). The pump is an output level
from 0 to 100%; it belongs in Intensity, and in Intensity the release costs one
DMX frame.

So a smoke button is safe when either is true: the pump channel is one QLC+
resets by itself, or the thing the button starts **carries its own off** - a
haze chaser alternating a fog step with an off step, or a SingleShot burst
whose last step writes the zero. Anything else is a tank waiting to empty into
a room, which is why this is an error and not a warning.
"""

from lxml import etree

from ..fog_offsets import fog_offsets
from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, iter_local
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph, lit, reach

RULE = "humo pegado"
# The one QLC+ zeroes every cycle. Everything else holds its last value.
RESET_GROUP = "intensity"


def check_smoke_restore(
    graph: ShowGraph, groups, root: etree._Element, states: set[int]
) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    findings: list[Finding] = []
    for button in iter_local(console, "Button"):
        function = find_local(button, "Function")
        if function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if function_id not in graph.functions:
            continue
        held = _pumps_held(graph, groups, function_id)
        if not held or _clears_itself(graph, groups, function_id, held):
            continue
        caption = button.attrib.get("Caption", "")
        for fixture_id in sorted(held):
            findings.append(
                Finding(
                    rule=RULE,
                    severity=ERROR,
                    function=graph.name(function_id),
                    message=(
                        f"el boton «{caption}» abre la bomba de humo en un canal "
                        "que QLC+ no reinicia solo - no esta en el grupo Intensity "
                        "- y la funcion no lo cierra: al soltar, la maquina sigue "
                        "tirando hasta vaciar el deposito"
                    ),
                    fixtures=(graph.capabilities[fixture_id].fixture.name,),
                )
            )
    return findings


def _pumps_held(graph: ShowGraph, groups, function_id: int) -> dict[int, set[int]]:
    """Fixture id -> the pump offsets this button raises that QLC+ will not clear."""
    held: dict[int, set[int]] = {}
    for fixture_id, written in reach(graph, groups, function_id).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None or not capability.is_smoke:
            continue
        offsets = {
            offset
            for offset in fog_offsets(capability)
            if offset in written
            and lit(written[offset])
            and capability.groups_by_offset[offset].lower() != RESET_GROUP
        }
        if offsets:
            held[fixture_id] = offsets
    return held


def _clears_itself(
    graph: ShowGraph,
    groups,
    function_id: int,
    held: dict[int, set[int]],
    seen: frozenset = frozenset(),
) -> bool:
    """Whether the thing this button starts carries its own "pump shut".

    A chaser alternating a fog step with an off step does - `Humo Auto` has run
    the haze that way for years, and the pump closes again a step later
    whatever anyone presses. A SingleShot burst does when its **last** step is
    the one that closes it. A Collection is as safe as the member that does, so
    the question recurses. A bare scene never does.
    """
    if function_id in seen:
        return False
    seen = seen | {function_id}
    steps = graph.members.get(function_id, ())
    if not steps:
        return False
    function = graph.functions[function_id]
    order = find_local(function, "RunOrder")
    single = (
        function.attrib.get("Type") == "Chaser"
        and order is not None
        and (order.text or "").strip() == "SingleShot"
    )
    candidates = [steps[-1]] if single else list(steps)
    return any(
        _shuts(graph, groups, step, held) or _clears_itself(graph, groups, step, held, seen)
        for step in candidates
    )


def _shuts(graph: ShowGraph, groups, step: int, held) -> bool:
    """Whether this one step writes zero to every pump offset that was raised."""
    if step not in graph.functions:
        return False
    written = driven_channels(graph.functions[step], graph.capabilities, groups)
    return all(
        written.get(fixture_id, {}).get(offset) == 0
        for fixture_id, offsets in held.items()
        for offset in offsets
    )
