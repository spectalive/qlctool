"""2026-09-27, Round 2 review: the cells a matrix can be seen on.

QLC+ paints a head's cyan, magenta and yellow when it has no red, green and
blue (rgbmatrix.cpp), so a CMY head is a cell; a head on a colour wheel is not.
"""

from qlctool import roles
from qlctool.rgb_cells import rgb_cells


class _Head:
    def __init__(self, *held):
        self.held = set(held)

    def has_role(self, role):
        return role in self.held


def test_a_cmy_head_is_a_cell_and_a_wheel_is_not():
    capabilities = {
        1: _Head(roles.RED, roles.GREEN, roles.BLUE),
        2: _Head(roles.CYAN, roles.MAGENTA, roles.YELLOW),
        3: _Head(roles.GOBO),
        4: _Head(roles.RED, roles.GREEN),
    }
    assert rgb_cells(capabilities, [4, 3, 2, 1, 5]) == [2, 1]
