"""A matrix drawn on a group whose rigged cells cannot show it.

2026-09-26, en-sala DMX audit (items 4 and 12): every `Cabezas` matrix left the
rigged rig exactly as it was. The group is the four 7R beams, which have a
colour wheel and no red, green or blue for a matrix to write, plus eight washes
the stage plot hides as spares in a flight case. Every cell a matrix could
paint was a spare, so `Fill Rojo`, `Alternate Verde Menta/Azul Profundo` and
the rest lit nothing anybody could see.

Read off the matrix's group, the capabilities of its cells and the Monitor's
`Hidden` flags (`rigged_fixture_ids`): an error when no cell is both rigged
and red-green-blue, a warning when most of the cells a matrix paints are
spares. A workspace with no Monitor counts every fixture as rigged.
"""

from lxml import etree

from ..fixture_group import fixture_groups
from ..rgb_cells import rgb_cells
from ..rigged_fixture_ids import rigged_fixture_ids
from ..xmlutil import find_local
from .finding import ERROR, WARNING, Finding
from .show_graph import ShowGraph

RULE_ID = "invisible_matrix"


def check_invisible_matrix(graph: ShowGraph, root: etree._Element) -> list[Finding]:
    """One finding per RGBMatrix whose rigged cells show little or nothing of it."""
    rigged = rigged_fixture_ids(root)
    groups = {group.group_id: group for group in fixture_groups(root)}
    findings: list[Finding] = []
    for function_id in sorted(graph.functions):
        function = graph.functions[function_id]
        element = find_local(function, "FixtureGroup")
        if function.attrib.get("Type") != "RGBMatrix" or element is None:
            continue
        group = groups.get(int((element.text or "-1").strip()))
        if group is None:
            continue
        painted = rgb_cells(graph.capabilities, group.fixture_ids)
        spares = [fixture_id for fixture_id in painted if fixture_id not in rigged]
        if len(spares) < len(painted) and 2 * len(spares) <= len(painted):
            continue
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=WARNING if len(spares) < len(painted) else ERROR,
                function=graph.name(function_id),
                message_id=(
                    "invisible_matrix_mostly_spares"
                    if len(spares) < len(painted)
                    else "invisible_matrix_no_cell"
                ),
                fields={"group": group.name, "spares": len(spares), "cells": len(painted)},
                fixtures=tuple(sorted(graph.capabilities[i].fixture.name for i in spares)),
            )
        )
    return findings
