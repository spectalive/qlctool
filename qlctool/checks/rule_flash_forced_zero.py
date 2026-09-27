"""A held flash forced LTP that writes an intensity lower than another button gives.

`ForceLTP` is what lets a held flash strobe a channel the level holds higher
(`rule_strobe_masked_by_htp`). It forces every value of the scene, the low ones
included: `Flash 100%` also wrote the smoke pumps 0, so once forced, holding
FLASH would have cut a smoke burst in progress. The ruling (D1, 2026-09-26): a
held flash neither starts nor stops smoke, and its pump pairs go.

The rule reads the wiring, the capabilities and the graph, never a name: a
Flash button with `ForceLTP` whose Scene writes a channel QLC+ merges HTP
(`htp_offsets`) lower than some other console button reaches on the same
channel cuts that button's output while it is held. Colour is left alone - a
colour's zeros are part of the colour a bank or a hit replaces. On a
strobe-role channel only a value that shuts the fixture counts
(`value_shuts`: the MiN Wash's "Closed", not a PAR's "no strobe"), and only
against a button that holds it lit without strobing: a flash that chooses not
to strobe over another that strobes is two hands, not a cut.
"""

from lxml import etree

from .. import roles
from ..vc.build_button import NO_FUNCTION
from ..xmlutil import find_local, iter_local
from .color_roles import COLOUR
from .finding import ERROR, Finding
from .fixture_names_of import fixture_names_of
from .htp_offsets import htp_offsets
from .show_graph import ShowGraph, reach
from .strobe_written import strobe_capable_offsets
from .value_shuts import value_shuts
from .value_strobes import value_strobes

RULE_ID = "flash_forced_zero"
FULL = 255


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
        lowered: dict[tuple[int, int], int] = {}
        for fixture_id, written in graph.driven_of(scene, groups).items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None:
                continue
            for offset, value in written.items():
                role = capability.roles_by_offset[offset]
                if value is None or offset not in htp.get(fixture_id, frozenset()):
                    continue
                if role in COLOUR:
                    continue
                if role == roles.STROBE and not value_shuts(capability, offset, value):
                    continue
                lowered[(fixture_id, offset)] = value
        if not lowered:
            continue
        cut: set[int] = set()
        cut_from: list[int] = []
        for other in sorted(entries):
            if other == function_id:
                continue
            driven = reach(graph, groups, other)
            hit: set[int] = set()
            for (fixture_id, offset), value in lowered.items():
                if offset not in driven.get(fixture_id, {}):
                    continue
                given = driven[fixture_id][offset]
                # An effect (None) may be anything, but nothing is above full.
                if value >= FULL or (given is not None and given <= value):
                    continue
                capability = graph.capabilities[fixture_id]
                strobing = strobe_capable_offsets(capability)
                if (
                    given is not None
                    and offset in strobing
                    and value_strobes(strobing[offset], given)
                ):
                    continue
                hit.add(fixture_id)
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
