"""A bank key that leaves some of the room on the colour beneath.

Keys 1-0 press the same colour in every bank at once, and a bank is one
fixture group's. The two CLB2.4 PARs and the four fog LED columns are in no
group, so while `1` was held the rig went red and those six stayed on the
colour the state was showing (en-sala DMX audit, 2026-09-26, item 6).

The rule reads bindings, capabilities and the graph, never a name: a key or
pad channel whose Flash buttons forced LTP (`forced_flash_triggers`) are all
pure colour takeovers (`colour_takeover_fixtures`: a whole colour on every RGB
fixture written, no dimmer) is a key that recolours the room, whether it
holds one colour or a split and whether it presses five banks or one. Every
rigged fixture with red, green and blue that some room state lights in colour
must be among the fixtures those scenes recolour; the ones missing keep the
old colour while the key is down.
"""

from lxml import etree

from .. import roles
from ..rigged_fixture_ids import rigged_fixture_ids
from .colour_takeover_fixtures import colour_takeover_fixtures
from .finding import ERROR, Finding
from .fixture_names_of import fixture_names_of
from .forced_flash_triggers import forced_flash_triggers
from .lit import lit
from .reach import reach
from .show_graph import ShowGraph

RULE_ID = "bank_key_coverage"
RGB = (roles.RED, roles.GREEN, roles.BLUE)


def check_bank_key_coverage(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    root: etree._Element,
    states: set[int],
) -> list[Finding]:
    triggers = forced_flash_triggers(root)
    if not triggers or not states:
        return []
    rigged = rigged_fixture_ids(root)
    coloured: set[int] = set()
    for state in states:
        for fixture_id, written in reach(graph, groups, state).items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None or fixture_id not in rigged:
                continue
            offsets = [o for role in RGB for o in capability.offsets_for_role(role)]
            if all(capability.offsets_for_role(r) for r in RGB) and any(
                o in written and lit(written[o]) for o in offsets
            ):
                coloured.add(fixture_id)
    findings: list[Finding] = []
    for (kind, trigger), functions in sorted(triggers.items()):
        covered: set[int] = set()
        for function_id in functions:
            function = graph.functions.get(function_id)
            recoloured = (
                colour_takeover_fixtures(graph, groups, function)
                if function is not None and function.attrib.get("Type") == "Scene"
                else None
            )
            if recoloured is None:
                break
            covered |= recoloured
        else:
            missing = coloured - covered
            if missing:
                findings.append(
                    Finding(
                        rule_id=RULE_ID,
                        severity=ERROR,
                        function=graph.name(min(functions)),
                        fixtures=fixture_names_of(graph, missing),
                        message_id=(
                            "bank_key_coverage_key" if kind == "key" else "bank_key_coverage_pad"
                        ),
                        fields={
                            "trigger": trigger,
                            "buttons": len(functions),
                            "count": len(missing),
                        },
                    )
                )
    return findings
