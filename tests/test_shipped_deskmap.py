"""The tablet's map that ships next to a show is the map of that show.

2026-09-24: `Vibra.desk.json` still named the ed1dac1 workspace after 3491a11
regenerated `Vibra.qxw`. 36 of its 144 widget ids and 141 function ids no
longer existed in the new show, so a tablet built from it would have pressed
the wrong buttons, and nothing had noticed.
"""

import json

import pytest
from rig_root import RIG_ROOT

from qlctool.deskmap import build_deskmap
from qlctool.library import FixtureLibrary
from qlctool.workspace import Workspace

SETUPS = RIG_ROOT / "QLC+ Setups"
SHIPPED = sorted(SETUPS.glob("*.desk.json"))


def test_at_least_one_map_ships():
    assert SHIPPED


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: p.name)
def test_the_shipped_map_is_rebuilt_byte_for_byte_from_its_workspace(path):
    shipped = json.loads(path.read_text(encoding="utf-8"))
    workspace_path = SETUPS / shipped["show"]["workspace"]
    rebuilt = build_deskmap(Workspace.load(workspace_path), FixtureLibrary.load(), workspace_path)
    assert shipped["show"]["sha256"] == rebuilt["show"]["sha256"], (
        f"{path.name} was built from another {workspace_path.name}; "
        f"run `qlctool deskmap --out '{path}' '{workspace_path}'`"
    )
    assert shipped == rebuilt
