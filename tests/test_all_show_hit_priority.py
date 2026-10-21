"""2026-10-21: every shipped programme must protect each tablet accent."""

import pytest
from rig_root import RIG_ROOT

from qlctool.capabilities_of import capabilities_of
from qlctool.checks.build_show_graph import build_show_graph
from qlctool.checks.rule_desk_bursts import check_desk_bursts
from qlctool.desk_burst_sources import desk_burst_sources
from qlctool.fixture_library import FixtureLibrary
from qlctool.names.default_names import default_names
from qlctool.workspace import Workspace


@pytest.mark.parametrize("name", ("Vibra.qxw", "Vibra-beats.qxw", "Vibra-split.qxw"))
def test_2026_10_21_all_programmes_guard_every_tablet_hit(name):
    workspace = Workspace.load(RIG_ROOT / "QLC+ Setups" / name)
    library = FixtureLibrary.load()
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    sources = desk_burst_sources(workspace.root, default_names())
    assert len(sources) == 25, (name, sorted(sources))
    assert not check_desk_bursts(graph, workspace.root), name
