"""A colour wheel's desk tile shows colours the wheel shows, step by step.

2026-10-19, from the en-sala round 1 night (2026-09-26): `swatches` read the
merged reach of a Chaser, which keeps the highest value of every channel
across all its steps, so `Pastel tenue` - a wheel of pastels - drew one white
tile, and the mix wheel gained a magenta no step ever lights.
"""

import pytest
from named_show import named_show
from rig_root import RIG_ROOT

from qlctool.build_deskmap import build_deskmap
from qlctool.capabilities_of import capabilities_of
from qlctool.checks.build_show_graph import build_show_graph
from qlctool.checks.group_fixtures import group_fixtures
from qlctool.fixture_library import FixtureLibrary
from qlctool.max_swatches import MAX_SWATCHES
from qlctool.reach_swatches import reach_swatches

WHEELS = ("colores-completos", "colores-simples", "pastel-tenue", "multicolor")


@pytest.fixture(scope="module")
def shown():
    workspace = named_show("Vibra.qxw")
    library = FixtureLibrary.load()
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    groups = group_fixtures(workspace.root)
    path = RIG_ROOT / "QLC+ Setups" / "Vibra.qxw"
    return graph, groups, build_deskmap(workspace, library, path)["controls"]


def _step_colours(graph, groups, chaser_id):
    ordered: list[str] = []
    for step_id in graph.members[chaser_id]:
        for colour in reach_swatches(graph, groups, step_id):
            if colour not in ordered:
                ordered.append(colour)
    return ordered


def test_2026_10_19_a_wheel_tile_shows_its_steps_in_order_not_their_merged_max(shown):
    graph, groups, controls = shown
    for key in WHEELS:
        control = controls[key]
        assert control["functionType"] == "Chaser"
        steps = _step_colours(graph, groups, control["function"])
        assert len(steps) > 1, key
        assert control["swatches"] == steps[:MAX_SWATCHES], key
        assert control["swatches"] != ["#ffffff"], key


def test_2026_10_19_the_merged_reach_would_draw_a_colour_no_step_shows(shown):
    """The bug put back: reading the chaser's merged reach gives the tile a
    colour outside every step, which is what the test above refuses."""
    graph, groups, controls = shown
    pastel = controls["pastel-tenue"]["function"]
    merged = reach_swatches(graph, groups, pastel)
    assert set(merged) - set(_step_colours(graph, groups, pastel))
