"""A small club, patched through the CLI: a different patch from Vibra's.

Three of Vibra's models in other numbers, addresses and groups, with no haze
machine and no controllers: six Vortex PC-64 RGB pars, two LED Beam moving
heads with no gobo or prism wheel, two Chauvet MiN Wash. Two groups: the pars
in a row, the four heads in a row. Verified by hand on 2026-09-25: the patch
loads, and before Task 2 `newshow` stopped at "no fixture in this workspace
has a gobo channel".
"""

import shutil
from pathlib import Path

from qlctool.cli import main

EMPTY = Path(__file__).resolve().parent / "data" / "empty-workspace.qxw"


def build_small_rig_patch(folder: Path) -> Path:
    """Write club-patch.qxw into `folder` and return it."""
    empty = folder / "empty.qxw"
    shutil.copy(EMPTY, empty)
    adds, address = [], 1
    for index in range(1, 7):
        adds += ["--add", f"Vortex|PC-64 LED S|Default|0|{address}|Par {index}"]
        address += 5
    for index in range(1, 3):
        adds += ["--add", f"LED Beam|Mini Led Moving Head|16 Channels|0|{address}|Beam {index}"]
        address += 16
    for index in range(1, 3):
        adds += ["--add", f"Chauvet|MiN Wash|13 Channel|0|{address}|Wash {index}"]
        address += 13
    patched = folder / "patched.qxw"
    groups = ["--group-new", "Pars=6x1", "--group-new", "Heads=4x1"]
    assert main(["patch", str(empty), *adds, *groups, "--out", str(patched)]) == 0
    cells = [arg for i in range(6) for arg in ("--group-add", f"0={i}@{i},0")]
    cells += [arg for i in range(6, 10) for arg in ("--group-add", f"1={i}@{i - 6},0")]
    out = folder / "club-patch.qxw"
    assert main(["patch", str(patched), *cells, "--out", str(out)]) == 0
    empty.unlink()
    patched.unlink()
    return out
