"""Laying a fixture group out in the order the room is in.

2026-08-31: `Cabezas` walked its four rigged beams 1916, 9694, 4405, 7205 mm
across the stage, and the split's `PAR` jumped twice. A matrix paints the cells
a group declares and half of QLC+'s scripts mean a direction, so every sweep
over those groups went left, far right, back to the middle - visible only as an
animation that never looked like a sweep.
"""

from pathlib import Path

import pytest

from qlctool.checks.rule_grid_order import check_grid_order
from qlctool.fixture_group import fixture_groups
from qlctool.repatch.group_sort import sort_group_by_stage
from qlctool.stage_x_positions import stage_x_positions
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, iter_local

REPO = Path(__file__).resolve().parents[3]
SHOWS = ("Vibra.qxw", "Vibra-beats.qxw", "Vibra-split.qxw")


def _group_element(root, group_id):
    return next(
        element
        for element in iter_local(root, "FixtureGroup")
        if element.attrib.get("ID") == str(group_id)
    )


def _row(root, group_id, y=0):
    element = _group_element(root, group_id)
    return [
        (int(head.attrib["X"]), int(head.attrib["Fixture"]))
        for head in findall_local(element, "Head")
        if int(head.attrib["Y"]) == y
    ]


def _group_id(root, name):
    return next(g.group_id for g in fixture_groups(root) if g.name == name)


@pytest.mark.parametrize("name", SHOWS)
def test_every_shipped_group_is_in_stage_order(name):
    """The rule has to be true of every workspace this repo ships, or it is
    only true of the one file it was written for."""
    workspace = Workspace.load(REPO / "QLC+ Setups" / name)

    assert not check_grid_order(workspace.root)


def test_sorting_puts_the_rigged_fixtures_left_to_right():
    workspace = Workspace.load(REPO / "QLC+ Setups" / "Vibra-split.qxw")
    root = workspace.root
    positions = stage_x_positions(root)
    group_id = _group_id(root, "Cabezas")
    # Put the row back in patch order, which is where it came from.
    element = _group_element(root, group_id)
    for cell, head in enumerate(
        sorted(
            findall_local(element, "Head"),
            key=lambda h: int(h.attrib["Fixture"]),
        )
    ):
        head.set("X", str(cell))
    assert check_grid_order(root), "the repro did not put the group out of order"

    sort_group_by_stage(root, group_id)

    placed = [
        positions[fixture_id]
        for _, fixture_id in sorted(_row(root, group_id))
        if fixture_id in positions
    ]
    assert placed == sorted(placed)
    assert not [f for f in check_grid_order(root) if f.function == "Cabezas"]


def test_unplaced_fixtures_go_last_and_keep_the_run_intact():
    """Eight of `Cabezas`' twelve members are spares the plot marks not rigged.
    A spare cannot be anywhere in a sweep, so it must not sit in the middle of
    one."""
    workspace = Workspace.load(REPO / "QLC+ Setups" / "Vibra-split.qxw")
    root = workspace.root
    positions = stage_x_positions(root)
    group_id = _group_id(root, "Cabezas")

    sort_group_by_stage(root, group_id)

    row = sorted(_row(root, group_id))
    placed = [x for x, fixture_id in row if fixture_id in positions]
    unplaced = [x for x, fixture_id in row if fixture_id not in positions]
    assert placed and unplaced
    assert max(placed) < min(unplaced)


def test_a_bars_segments_keep_the_bars_own_order():
    """Eight segments of one LED bar share a single stage X, so the stage has
    nothing to say about which comes first - the bar does."""
    workspace = Workspace.load(REPO / "QLC+ Setups" / "Vibra-split.qxw")
    root = workspace.root
    group_id = _group_id(root, "BarrasLed")
    element = _group_element(root, group_id)
    before = [
        (int(h.attrib["X"]), int(h.attrib["Y"]), int(h.attrib["Fixture"]), int(h.text or 0))
        for h in findall_local(element, "Head")
    ]

    sort_group_by_stage(root, group_id)

    after = [
        (int(h.attrib["X"]), int(h.attrib["Y"]), int(h.attrib["Fixture"]), int(h.text or 0))
        for h in findall_local(element, "Head")
    ]
    assert sorted(after) == sorted(before)


def test_sorting_a_workspace_with_no_positions_is_refused():
    workspace = Workspace.load(REPO / "QLC+ Setups" / "Vibra-split.qxw")
    engine = find_local(workspace.root, "Engine")
    engine.remove(find_local(engine, "Monitor"))

    with pytest.raises(ValueError, match="no fixture positions"):
        sort_group_by_stage(workspace.root, 0)


def test_two_fixtures_at_one_position_keep_the_order_somebody_chose():
    """A tie on stage X breaks on the cell the head already had, never on the
    head index: sorting by head index interleaves two co-located fixtures'
    segments into each other (found in review, 2026-08-31)."""
    workspace = Workspace.load(REPO / "QLC+ Setups" / "Vibra-split.qxw")
    root = workspace.root
    group_id = _group_id(root, "BarrasLed")
    element = _group_element(root, group_id)
    # Put both bars on one row, at one position, alternating - the shape the
    # head-index key scrambled.
    heads = findall_local(element, "Head")
    for cell, head in enumerate(heads):
        head.set("X", str(cell))
        head.set("Y", "0")
    before = [
        (int(h.attrib["Fixture"]), int(h.text or 0))
        for h in sorted(heads, key=lambda h: int(h.attrib["X"]))
    ]

    sort_group_by_stage(root, group_id)

    after = [
        (int(h.attrib["Fixture"]), int(h.text or 0))
        for h in sorted(findall_local(element, "Head"), key=lambda h: int(h.attrib["X"]))
    ]
    assert after == before


def test_a_spare_in_the_middle_of_a_row_is_reported():
    """A cell holding a fixture the plot never rigged is not neutral - the
    matrix paints it and nothing lights, so it is a hole in every sweep. The
    rule has to see what `--group-sort` would move (found in review,
    2026-08-31)."""
    workspace = Workspace.load(REPO / "QLC+ Setups" / "Vibra-split.qxw")
    root = workspace.root
    positions = stage_x_positions(root)
    group_id = _group_id(root, "Cabezas")
    element = _group_element(root, group_id)
    heads = {int(h.attrib["X"]): h for h in findall_local(element, "Head")}
    rigged = [x for x, h in heads.items() if int(h.attrib["Fixture"]) in positions]
    spare = next(x for x, h in heads.items() if int(h.attrib["Fixture"]) not in positions)
    assert not check_grid_order(root)

    heads[min(rigged)].set("X", str(spare))
    heads[spare].set("X", str(min(rigged)))

    assert [f for f in check_grid_order(root) if f.function == "Cabezas"]
