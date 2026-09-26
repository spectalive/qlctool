"""Round G review, 2026-09-26: the parse cache 34 rules now share.

`ShowGraph.driven_of` hands every rule the same parsed answer, so a rule
that wrote into it would change what every later rule reads: the answer is
read-only at both levels. And a `groups` mapping is keyed by its identity,
so each `{}` a rule passed added one entry to `groups_keys`.
"""

import pytest
from rig_root import RIG_ROOT

from qlctool.capabilities_of import capabilities_of
from qlctool.checks.show_graph import build_show_graph
from qlctool.library import FixtureLibrary
from qlctool.workspace import Workspace


@pytest.fixture(scope="module")
def graph_and_scene():
    root = Workspace.load(RIG_ROOT / "QLC+ Setups" / "Vibra.qxw").root
    graph = build_show_graph(root, capabilities_of(root, FixtureLibrary.load()))
    scene = next(
        f for f in graph.functions.values() if f.get("Type") == "Scene" and graph.driven_of(f, {})
    )
    return graph, scene


def test_2026_09_26_what_the_cache_hands_out_cannot_be_written(graph_and_scene):
    graph, scene = graph_and_scene
    driven = graph.driven_of(scene, {})
    fixture_id, pairs = next(iter(driven.items()))
    with pytest.raises(TypeError):
        driven[fixture_id] = {}  # type: ignore[index]
    with pytest.raises(TypeError):
        pairs[0] = 255  # type: ignore[index]
    assert graph.driven_of(scene, {}) == driven


def test_2026_09_26_an_empty_groups_mapping_adds_no_key(graph_and_scene):
    graph, scene = graph_and_scene
    before = len(graph.groups_keys)
    for _ in range(50):
        graph.driven_of(scene, {})
    assert len(graph.groups_keys) == before
