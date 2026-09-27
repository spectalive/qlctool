"""2026-09-27: one multiplier over layers that already run one length flattens nothing.

A lone MiN Wash's tap dial lists its four colour wheels and nothing else, all
stepping at the one beat; the rule read four equal multipliers as a flattened
console. It now reads the layers' own durations: equal layers under one
multiplier keep their length, unequal ones under one multiplier do not.
"""

from pathlib import Path

import pytest
from single_shape_rig import build_single_shape_patch

from qlctool.checks.rule_tap_dial import RULE_ID, check_tap_dial
from qlctool.cli import main
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, iter_local

LONE_WASH = ("Chauvet|MiN Wash|13 Channel|0|{address}|Wash {index}", 1, 13)


@pytest.fixture(scope="module")
def show(tmp_path_factory) -> Path:
    folder = tmp_path_factory.mktemp("lone")
    out = folder / "show.qxw"
    assert (
        main(["newshow", str(build_single_shape_patch(folder, *LONE_WASH)), "--out", str(out)]) == 0
    )
    return out


def _tapped_dial(root):
    console = find_local(root, "VirtualConsole")
    assert console is not None
    return next(
        d
        for d in iter_local(console, "SpeedDial")
        if any(i.get("ID") == "1" for i in findall_local(d, "Input"))
    )


def test_2026_09_27_equal_layers_under_one_multiplier_pass(show):
    root = Workspace.load(show).root
    dial = _tapped_dial(root)
    listed = findall_local(dial, "Function")
    assert len(listed) >= 3
    assert len({f.get("Duration") for f in listed}) == 1
    assert [f for f in check_tap_dial(root) if f.rule_id == RULE_ID] == []


def test_2026_09_27_unequal_layers_under_one_multiplier_still_flatten(show):
    root = Workspace.load(show).root
    dial = _tapped_dial(root)
    first_id = (findall_local(dial, "Function")[0].text or "").strip()
    engine = find_local(root, "Engine")
    assert engine is not None
    function = next(f for f in iter_local(engine, "Function") if f.get("ID") == first_id)
    speed = find_local(function, "Speed")
    assert speed is not None
    speed.set("Duration", str(int(speed.get("Duration", "0")) * 2 + 100))
    assert [f.rule_id for f in check_tap_dial(root)] == [RULE_ID]
