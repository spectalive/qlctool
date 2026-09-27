"""A held strobe on an HTP channel that the running level out-bids.

The two MiN Wash have one channel for dimmer and strobe, and it is in the
Intensity group, so QLC+ merges it HTP. The levels hold it at 255 ("Open"),
`Strobo Rapido` writes 236 and the flashes the same: max(255, 236) is 255, and
the MiN Wash never strobed while any level ran (en-sala DMX audit,
2026-09-26, items 7 and 16). The buttons carried Override, which only orders
the faders; the lower value is still dropped unless the writer forces LTP
(`Universe::write`).

The rule reads the wiring, the channel groups and the graph, never a name: a
Flash button without `ForceLTP` whose Scene writes a strobing value
(`strobe_written`) on a channel QLC+ merges HTP (`htp_offsets`), where some
room state reaches a higher definite value on the same channel, is a strobe
that cannot show while that state runs.
"""

from lxml import etree

from ..vc.build_button import NO_FUNCTION
from ..xmlutil import find_local, iter_local
from .finding import ERROR, Finding
from .fixture_names_of import fixture_names_of
from .htp_offsets import htp_offsets
from .show_graph import ShowGraph, reach
from .strobe_written import strobe_capable_offsets, value_strobes

RULE_ID = "strobe_masked_by_htp"


def check_strobe_masked_by_htp(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    root: etree._Element,
    states: set[int],
    entries: dict[int, str],
) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None or not states:
        return []
    htp = htp_offsets(root, graph.capabilities)
    under = {state: reach(graph, groups, state) for state in sorted(states)}
    findings: list[Finding] = []
    seen: set[int] = set()
    for button in iter_local(console, "Button"):
        action = find_local(button, "Action")
        function = find_local(button, "Function")
        if action is None or (action.text or "").strip() != "Flash" or function is None:
            continue
        if action.get("ForceLTP") == "1":
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if function_id == NO_FUNCTION or function_id in seen:
            continue
        seen.add(function_id)
        scene = graph.functions.get(function_id)
        if scene is None or scene.attrib.get("Type") != "Scene":
            continue  # rule_flash_scene already reports that wiring
        masked: set[int] = set()
        outbid_by: list[int] = []
        for fixture_id, written in graph.driven_of(scene, groups).items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None:
                continue
            for offset, strobing in strobe_capable_offsets(capability).items():
                value = written.get(offset)
                if value is None or offset not in htp.get(fixture_id, frozenset()):
                    continue
                if not value_strobes(strobing, value):
                    continue
                for state, driven in under.items():
                    level = driven.get(fixture_id, {}).get(offset)
                    if level is not None and level > value:
                        masked.add(fixture_id)
                        outbid_by.append(state)
                        break
        if masked:
            state = outbid_by[0]
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(function_id),
                    fixtures=fixture_names_of(graph, masked),
                    message_id="strobe_masked_by_htp_outbid",
                    fields={"count": len(masked), "state": entries.get(state, graph.name(state))},
                )
            )
    return findings
