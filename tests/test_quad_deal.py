"""2026-09-25: the four-colour deal put two opposite hues on a group of two pars.

The same session as the small club: a rig whose only colour group is two
Vortex pars got `Rig 4 Colores 4` with one par yellow and the other blue, and
`check` reported `complementarios en un mismo lavado`. The deal walked blue,
red, green, yellow over the rig in patch order, so a group of two always took
two neighbours of that cycle, and yellow's neighbour is blue.
"""

import shutil
from pathlib import Path

from qlctool.checks.rule_split_complementary import RULE
from qlctool.checks.run import check_workspace
from qlctool.cli import main
from qlctool.library import FixtureLibrary
from qlctool.workspace import Workspace

EMPTY = Path(__file__).resolve().parent / "data" / "empty-workspace.qxw"


def _two_par_patch(folder: Path) -> Path:
    """Two Vortex pars in a group of their own, and the small club's four heads."""
    empty = folder / "empty.qxw"
    shutil.copy(EMPTY, empty)
    adds = [
        "--add",
        "Vortex|PC-64 LED S|Default|0|1|Par 1",
        "--add",
        "Vortex|PC-64 LED S|Default|0|6|Par 2",
    ]
    address = 11
    for index in range(1, 3):
        adds += ["--add", f"LED Beam|Mini Led Moving Head|16 Channels|0|{address}|Beam {index}"]
        address += 16
    for index in range(1, 3):
        adds += ["--add", f"Chauvet|MiN Wash|13 Channel|0|{address}|Wash {index}"]
        address += 13
    patched = folder / "patched.qxw"
    groups = ["--group-new", "Pars=2x1", "--group-new", "Heads=4x1"]
    assert main(["patch", str(empty), *adds, *groups, "--out", str(patched)]) == 0
    cells = [arg for i in range(2) for arg in ("--group-add", f"0={i}@{i},0")]
    cells += [arg for i in range(2, 6) for arg in ("--group-add", f"1={i}@{i - 2},0")]
    out = folder / "two-par-patch.qxw"
    assert main(["patch", str(patched), *cells, "--out", str(out)]) == 0
    return out


def test_2026_09_25_a_group_of_two_gets_no_complementary_pair(tmp_path):
    out = tmp_path / "two-pars.qxw"
    assert main(["newshow", str(_two_par_patch(tmp_path)), "--out", str(out)]) == 0
    findings = check_workspace(Workspace.load(out), FixtureLibrary.load())
    assert [str(f) for f in findings if f.rule == RULE] == []


def _quad_colours():
    from qlctool.generate.quad_color_scenes import QUAD_COLORS
    from qlctool.names.default_names import default_names
    from qlctool.palette import PALETTE

    return [PALETTE[default_names().display(identifier)] for identifier in QUAD_COLORS]


def test_2026_09_25_a_larger_group_on_opposite_seats_is_re_dealt():
    """2026-09-25, review of the fix above: a group of four whose members sit at
    patch indices 0, 3, 4 and 7 was dealt blue, yellow, blue, yellow - the same
    split twice - because only groups of exactly two were re-dealt.
    """
    from qlctool.generate.opposite_split import opposite_split
    from qlctool.generate.quad_seats import quad_seats

    colours = _quad_colours()
    dealt = list(range(100, 108))
    group = (100, 103, 104, 107)
    assert opposite_split([0, 3, 4, 7], colours)
    seats = quad_seats(dealt, {1: group}, colours)
    assert not opposite_split([seats[m] for m in group], colours)
    # Nobody outside the group moves.
    assert all(seats[m] == m - 100 for m in dealt if m not in group)


def test_2026_09_25_a_fixture_in_two_groups_is_seated_by_the_higher_id():
    """Same review: a fixture in two clashing groups moved depending on the
    order the groups were visited in. They are visited in ascending id, so
    fixture 103 ends where group 2 puts it, whatever order they are given in.
    Since the re-deal repeats until no group is split (re-review, same day),
    group 1 is dealt again around 103's final seat, so 104 sits at 4.
    """
    from qlctool.generate.quad_seats import quad_seats

    colours = _quad_colours()
    dealt = [100, 101, 102, 103, 104]
    expected = {100: 0, 101: 1, 102: 2, 103: 2, 104: 4}
    assert quad_seats(dealt, {2: (100, 103), 1: (103, 104)}, colours) == expected
    assert quad_seats(dealt, {1: (103, 104), 2: (100, 103)}, colours) == expected


def test_2026_09_25_no_group_is_left_split_after_the_re_deal():
    """2026-09-25, re-review of b4eb0c6: a fixture in two clashing groups could
    be moved back onto a split by the higher group, and nothing re-checked the
    final seats. The pass now repeats until no group is split.
    """
    from qlctool.generate.opposite_split import opposite_split
    from qlctool.generate.quad_seats import quad_seats

    colours = _quad_colours()
    dealt = list(range(100, 112))
    layouts = [
        {1: (100, 103), 2: (103, 104, 107)},
        {1: (100, 103, 104, 107), 2: (107, 110), 3: (103, 110)},
        {1: (101, 104), 2: (104, 105, 108), 3: (108, 111)},
        {5: (100, 111), 4: (103, 108), 3: (100, 103), 2: (108, 111)},
    ]
    for groups in layouts:
        seats = quad_seats(dealt, groups, colours)
        for members in groups.values():
            assert not opposite_split([seats[m] for m in members], colours), groups
