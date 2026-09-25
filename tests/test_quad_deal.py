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
