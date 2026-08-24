"""Building a fresh show from the rig: the consolidation the owner asked for."""

from pathlib import Path

import pytest

from qlctool.fixture import patched_fixtures
from qlctool.generate.canonical_show import (
    SHOW_ALGORITHMS,
    SHOW_COLORS,
    build_canonical_show,
)
from qlctool.library import FixtureLibrary
from qlctool.patch_conflicts import patch_conflicts
from qlctool.validate import qlcplus_binary, validate_workspace
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, localname

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"


def test_a_fresh_show_keeps_the_rig_and_nothing_else(tmp_path):
    ws = Workspace.load(SHOW)
    library = FixtureLibrary.load()

    show = build_canonical_show(ws, library)

    out = tmp_path / "fresh.qxw"
    ws.save(out)
    reloaded = Workspace.load(out).root

    assert len(patched_fixtures(reloaded)) == 27
    assert patch_conflicts(reloaded) == []

    functions = [
        f for f in find_local(reloaded, "Engine") if localname(f) == "Function"
    ]
    assert len(functions) == show.function_count
    # 3 groups x algorithms x colours, and no leftovers from the old show.
    assert len(show.matrix_ids) == 3 * len(SHOW_ALGORITHMS) * len(SHOW_COLORS)
    assert len(show.scene_ids) == len(SHOW_COLORS)
    assert len(show.efx_ids) == 7
    assert len(show.button_ids) == show.function_count


@pytest.mark.skipif(
    qlcplus_binary() is None, reason="QLC+ is not installed on this machine"
)
def test_qlcplus_loads_a_fresh_show(tmp_path):
    ws = Workspace.load(SHOW)
    build_canonical_show(ws, FixtureLibrary.load())
    out = tmp_path / "fresh.qxw"
    ws.save(out)

    result = validate_workspace(out)

    assert result.ok, result.describe()
