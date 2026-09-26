"""A held flash forced LTP that writes zero where another button gives light.

`ForceLTP` is what lets a held flash strobe a channel the level holds higher
(`rule_strobe_masked_by_htp`). It forces every value of the scene, zeros
included: `Flash 100%` also wrote the smoke pumps 0, so once forced, holding
FLASH would have cut a smoke burst in progress. The ruling (D1, 2026-09-26): a
held flash neither starts nor stops smoke, and its pump pairs go.

The rule reads the wiring, the channel groups and the graph, never a name: a
Flash button with `ForceLTP` whose Scene writes 0 on a channel QLC+ merges HTP
(`htp_offsets`) that is neither colour nor strobe - a colour's zeros are part
of the colour a bank or a hit replaces, and a strobe channel's zero is the
flash choosing not to strobe, as the plain bass hit does - where some other
console button reaches a lit value on the same channel, cuts that button's
output while it is held: a dimmer, or a smoke pump.
"""

from lxml import etree

from .. import roles
from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, iter_local
from .color_roles import COLOUR
from .finding import ERROR, Finding
from .fixture_names_of import fixture_names_of
from .htp_offsets import htp_offsets
from .show_graph import ShowGraph, lit, reach

RULE_ID = "flash_forced_zero"


def check_flash_forced_zero(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    root: etree._Element,
    entries: dict[int, str],
) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    htp = htp_offsets(root, graph.capabilities)
    findings: list[Finding] = []
    seen: set[int] = set()
    for button in iter_local(console, "Button"):
        action = find_local(button, "Action")
        function = find_local(button, "Function")
        if action is None or (action.text or "").strip() != "Flash" or function is None:
            continue
        if action.get("ForceLTP") != "1":
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if function_id == NO_FUNCTION or function_id in seen:
            continue
        seen.add(function_id)
        scene = graph.functions.get(function_id)
        if scene is None or scene.attrib.get("Type") != "Scene":
            continue  # rule_flash_scene already reports that wiring
        zeros = {
            (fixture_id, offset)
            for fixture_id, written in graph.driven_of(scene, groups).items()
            if (capability := graph.capabilities.get(fixture_id)) is not None
            for offset, value in written.items()
            if value == 0
            and offset in htp.get(fixture_id, frozenset())
            and capability.roles_by_offset[offset] not in (*COLOUR, roles.STROBE)
        }
        if not zeros:
            continue
        cut: set[int] = set()
        cut_from: list[int] = []
        for other in sorted(entries):
            if other == function_id:
                continue
            driven = reach(graph, groups, other)
            hit = {f for f, o in zeros if o in driven.get(f, {}) and lit(driven[f][o])}
            if hit - cut:
                cut |= hit
                cut_from.append(other)
        if cut:
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(function_id),
                    fixtures=fixture_names_of(graph, cut),
                    message_id="flash_forced_zero_cuts",
                    fields={"count": len(cut), "button": entries[cut_from[0]]},
                )
            )
    return findings
