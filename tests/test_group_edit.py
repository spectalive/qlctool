"""Editing a fixture group: its grid, and who sits in it.

Group membership is not decoration. Colour banks and matrices are both built
*per group*, so a fixture in no group gets only the handful of rig-wide scenes -
which is how two of the four pixel panels ended up with 7 scene values against
their neighbours' 47.
"""

from pathlib import Path

import pytest

from qlctool.repatch.group_head import add_group_head
from qlctool.repatch.group_size import set_group_size
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, iter_local

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "Vibra.qxw"


def _group(root, group_id):
    return next(e for e in iter_local(root, "FixtureGroup") if e.attrib.get("ID") == str(group_id))


@pytest.fixture
def root():
    return Workspace.load(SHOW).root


def test_the_barrasled_grid_covers_every_head_it_holds(root):
    """The bug this was written for: 8x2 declared over three rows of heads, so
    row 2 was unreachable by any matrix in the show."""
    group = _group(root, 0)
    size = find_local(group, "Size")
    width, height = int(size.attrib["X"]), int(size.attrib["Y"])
    for head in findall_local(group, "Head"):
        assert int(head.attrib["X"]) < width
        assert int(head.attrib["Y"]) < height


def test_all_four_pixel_panels_are_in_a_group_of_their_own(root):
    """They left BarrasLed on 2026-08-26: sharing a grid with the two bars made
    them four cells of the bars' picture, dark through half of every sweep."""
    panels = _group(root, 3)
    members = {int(h.attrib["Fixture"]) for h in findall_local(panels, "Head")}
    assert members == {24, 25, 27, 28}
    bars = {int(h.attrib["Fixture"]) for h in findall_local(_group(root, 0), "Head")}
    assert not bars & {24, 25, 27, 28}


def test_a_size_that_would_orphan_a_head_is_refused(root):
    with pytest.raises(ValueError, match="outside the grid"):
        set_group_size(root, 0, 8, 1)  # BarrasLed is 8x2, two rows of bar


def test_a_cell_outside_the_grid_is_refused(root):
    with pytest.raises(ValueError, match="outside group"):
        add_group_head(root, 0, 12, x=8, y=0)


def test_an_occupied_cell_is_refused(root):
    with pytest.raises(ValueError, match="already holds"):
        add_group_head(root, 0, 12, x=0, y=0)


def test_an_unpatched_fixture_is_refused(root):
    with pytest.raises(ValueError, match="not patched"):
        add_group_head(root, 0, 99, x=6, y=1)


def test_an_unknown_group_is_refused(root):
    with pytest.raises(KeyError):
        add_group_head(root, 77, 12, x=0, y=0)


def test_a_head_already_in_the_group_is_refused(root):
    """Fixture 12 is already in the PAR group. A head in two cells of one group
    is almost always a slip, not a mirror."""
    set_group_size(root, 2, 8, 1)  # PAR is 7x1 and full; make room first
    with pytest.raises(ValueError, match="already in group"):
        add_group_head(root, 2, 12, x=7, y=0)


def test_growing_the_grid_then_adding_works(root):
    set_group_size(root, 2, 8, 1)  # the PAR group, 7x1 with 7 heads
    add_group_head(root, 2, 24, x=7, y=0)
    group = _group(root, 2)
    placed = [h for h in findall_local(group, "Head") if h.attrib["Fixture"] == "24"]
    assert len(placed) == 1
    assert placed[0].text == "0"
