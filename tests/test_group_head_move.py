"""Moving a head inside a fixture group, and the three ways that is refused.

2026-08-25: laying the split show's `PAR` group out by hand was impossible -
`add_group_head` refuses a head it has already placed, and the only way round it
was to remove the fixture and add it back, which `remove_group_head` refuses
outright when the fixture is the last one in the group. So the group shipped as
a 7x3 grid with the CLB2.4 heads bolted to the right of the PC-64 block instead
of the 8x2 that reads like the rig.
"""

from pathlib import Path

import pytest

from qlctool.fixture_group import fixture_groups
from qlctool.repatch.group_head_move import move_group_head
from qlctool.repatch.group_size import set_group_size
from qlctool.workspace import Workspace

REPO = Path(__file__).resolve().parents[3]
# The current patch, not DeluxeEventos2: the old workspace declares BarrasLed
# as 8x2 while holding heads at y=2, so no legal resize can free a cell there.
SHOW = REPO / "QLC+ Setups" / "Vibra-split.qxw"


def _group(root, name):
    return next(g for g in fixture_groups(root) if g.name == name)


def _element(root, group_id):
    return next(
        element for element in root.iter()
        if element.tag.rpartition("}")[2] == "FixtureGroup"
        and int(element.attrib["ID"]) == group_id
    )


def _cells(root, name):
    group = _element(root, _group(root, name).group_id)
    return {
        (int(head.attrib["X"]), int(head.attrib["Y"])): int(
            head.attrib["Fixture"]
        )
        for head in group.iter()
        if head.tag.rpartition("}")[2] == "Head"
    }


def _declared_size(root, name):
    element = _element(root, _group(root, name).group_id)
    size = next(
        child for child in element
        if child.tag.rpartition("}")[2] == "Size"
    )
    return int(size.attrib["X"]), int(size.attrib["Y"])


def _with_a_free_cell(root, name):
    """`BarrasLed` ships with every cell of its grid taken, so widen it by one
    column - a move needs somewhere to move to."""
    width, height = _declared_size(root, name)
    set_group_size(root, _group(root, name).group_id, width + 1, height)
    return (width, 0)


def test_a_head_moves_to_a_free_cell_and_nothing_else_shifts():
    workspace = Workspace.load(SHOW)
    before = _cells(workspace.root, "BarrasLed")
    group = _group(workspace.root, "BarrasLed")
    target = _with_a_free_cell(workspace.root, "BarrasLed")
    origin, fixture_id = next(iter(before.items()))

    was = move_group_head(
        workspace.root, group.group_id, fixture_id, *target
    )

    after = _cells(workspace.root, "BarrasLed")
    assert was == origin
    assert after[target] == fixture_id
    assert origin not in after
    assert after == {**{c: f for c, f in before.items() if c != origin},
                     target: fixture_id}


def test_moving_onto_an_occupied_cell_is_refused():
    """Silently overwriting a placement would move a head out of every pattern
    it appears in, with nothing to say so."""
    workspace = Workspace.load(SHOW)
    group = _group(workspace.root, "BarrasLed")
    cells = _cells(workspace.root, "BarrasLed")
    (first, fixture_id), (occupied, _) = list(cells.items())[:2]

    with pytest.raises(ValueError, match="already holds fixture"):
        move_group_head(workspace.root, group.group_id, fixture_id, *occupied)

    assert _cells(workspace.root, "BarrasLed")[first] == fixture_id


def test_moving_off_the_grid_is_refused():
    workspace = Workspace.load(SHOW)
    group = _group(workspace.root, "BarrasLed")
    fixture_id = next(iter(_cells(workspace.root, "BarrasLed").values()))

    width, height = _declared_size(workspace.root, "BarrasLed")

    with pytest.raises(ValueError, match="outside group"):
        move_group_head(
            workspace.root, group.group_id, fixture_id, width, height - 1,
        )


def test_moving_a_head_that_is_not_in_the_group_is_refused():
    workspace = Workspace.load(SHOW)
    group = _group(workspace.root, "BarrasLed")
    missing = max(group.fixture_ids) + 900
    target = _with_a_free_cell(workspace.root, "BarrasLed")

    with pytest.raises(ValueError, match="is not in group"):
        move_group_head(workspace.root, group.group_id, missing, *target)


def test_a_named_head_moves_and_its_siblings_stay():
    """The LED bars are one fixture with sixteen heads, so a mover that only
    ever addressed head 0 could not lay that group out at all (2026-08-31)."""
    workspace = Workspace.load(SHOW)
    group = _group(workspace.root, "BarrasLed")
    before = _cells(workspace.root, "BarrasLed")
    target = _with_a_free_cell(workspace.root, "BarrasLed")
    fixture_id = before[(5, 0)]

    was = move_group_head(
        workspace.root, group.group_id, fixture_id, *target, head=5
    )

    after = _cells(workspace.root, "BarrasLed")
    assert was == (5, 0)
    assert after[target] == fixture_id
    assert (5, 0) not in after
    assert after[(4, 0)] == before[(4, 0)]
