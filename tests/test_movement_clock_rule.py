"""2026-10-21: separate automatic movement clocks must be visible to check."""

from lxml import etree

from qlctool.checks.rule_movement_clock import check_movement_clock
from qlctool.checks.show_graph import ShowGraph


def test_2026_10_21_two_concurrent_random_shape_rotations_drift():
    functions = {
        identifier: etree.Element("Function", ID=str(identifier), Type=kind, Name=str(identifier))
        for identifier, kind in [
            (1, "Collection"),
            (2, "Chaser"),
            (3, "Chaser"),
            (4, "EFX"),
            (5, "EFX"),
        ]
    }
    members = {1: (2, 3), 2: (4,) * 7, 3: (5,) * 7}
    graph = ShowGraph(functions=functions, members=members)
    findings = check_movement_clock(graph)
    assert len(findings) == 1
    assert findings[0].rule_id == "movement_clock"
    assert findings[0].fields == {"count": 2}
    functions[1].set("Type", "Chaser")
    assert check_movement_clock(graph) == []
    functions[1].set("Type", "Collection")
    members[1] = (2,)
    assert check_movement_clock(ShowGraph(functions=functions, members=members)) == []
    members[1] = (2, 3)
    members[3] = (5,) * 6
    assert check_movement_clock(ShowGraph(functions=functions, members=members)) == []
    members[3] = (5,) * 7
    functions[5].set("Type", "Scene")
    assert check_movement_clock(ShowGraph(functions=functions, members=members)) == []
    assert check_movement_clock(ShowGraph(functions={}, members={})) == []
