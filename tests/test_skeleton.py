"""Stripping a show back to its patch, the starting point for a fresh one."""

from pathlib import Path

import pytest

from qlctool.fixture import patched_fixtures
from qlctool.fixture_group import fixture_groups
from qlctool.patch_conflicts import patch_conflicts
from qlctool.skeleton import strip_to_skeleton
from qlctool.validate import qlcplus_binary, validate_workspace
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, localname

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"


def _engine_children(root):
    return [localname(c) for c in find_local(root, "Engine")]


def test_skeleton_keeps_the_rig_and_drops_the_show(tmp_path):
    ws = strip_to_skeleton(Workspace.load(SHOW))

    out = tmp_path / "skeleton.qxw"
    ws.save(out)
    reloaded = Workspace.load(out).root

    kinds = set(_engine_children(reloaded))
    assert "Function" not in kinds
    assert kinds <= {
        "InputOutputMap", "Fixture", "FixtureGroup", "ChannelsGroup", "Monitor"
    }

    # The rig survives intact.
    assert len(patched_fixtures(reloaded)) == 27
    assert [g.name for g in fixture_groups(reloaded)] == [
        "BarrasLed", "Cabezas", "PAR"
    ]
    assert patch_conflicts(reloaded) == []

    # The console is emptied but still well-formed.
    frame = find_local(find_local(reloaded, "VirtualConsole"), "Frame")
    assert [localname(c) for c in frame] == ["Appearance"]


@pytest.mark.skipif(
    qlcplus_binary() is None, reason="QLC+ is not installed on this machine"
)
def test_qlcplus_loads_a_skeleton(tmp_path):
    ws = strip_to_skeleton(Workspace.load(SHOW))
    out = tmp_path / "skeleton.qxw"
    ws.save(out)

    result = validate_workspace(out)

    assert result.ok, result.describe()
