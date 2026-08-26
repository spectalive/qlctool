"""Taking a fixture out of a group, and the two ways that can go wrong."""

from pathlib import Path

import pytest

from qlctool.fixture_group import fixture_groups
from qlctool.repatch.group_head_remove import remove_group_head
from qlctool.workspace import Workspace

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"


def _group(root, name):
    return next(g for g in fixture_groups(root) if g.name == name)


def test_removing_a_fixture_leaves_the_others_where_they_were():
    """A matrix paints the grid the group declares, so the survivors must not
    move: closing the gap would change where every remaining head sits in
    every pattern."""
    workspace = Workspace.load(SHOW)
    group = _group(workspace.root, "BarrasLed")
    victim = group.fixture_ids[-1]
    before = {
        fixture_id for fixture_id in group.fixture_ids if fixture_id != victim
    }

    removed = remove_group_head(workspace.root, group.group_id, victim)

    after = _group(workspace.root, "BarrasLed")
    assert removed >= 1
    assert set(after.fixture_ids) == before
    assert (after.width, after.height) == (group.width, group.height)


def test_removing_a_fixture_that_is_not_in_the_group_is_refused():
    workspace = Workspace.load(SHOW)
    group = _group(workspace.root, "BarrasLed")
    missing = max(group.fixture_ids) + 900
    with pytest.raises(ValueError, match="not in group"):
        remove_group_head(workspace.root, group.group_id, missing)


def test_emptying_a_group_is_refused():
    """An empty group generates a matrix that paints nothing."""
    workspace = Workspace.load(SHOW)
    group = _group(workspace.root, "BarrasLed")
    for fixture_id in group.fixture_ids[:-1]:
        remove_group_head(workspace.root, group.group_id, fixture_id)
    with pytest.raises(ValueError, match="no heads at all"):
        remove_group_head(
            workspace.root, group.group_id, group.fixture_ids[-1]
        )
