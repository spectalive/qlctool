"""A colour wheel's desk tile shows colours the wheel shows, step by step.

2026-10-19, from the en-sala round 1 night (2026-09-26): `swatches` read the
merged reach of a Chaser, which keeps the highest value of every channel
across all its steps, so `Pastel tenue` - a wheel of pastels - drew one white
tile. The first fix read only a Chaser step by step, so `Rueda Mezcla` - a
Collection of five wheels - and the AUTO/tranquilo/fiesta/locura looks over
`Rueda Colores` still drew #ffffff (review of 10c41ed, 2026-10-19).
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
OVER_WHEELS = ("mezcla", "auto", "tranquilo", "fiesta", "locura")


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


def _colours_any_step_shows(graph, groups, function_id):
    """Every colour one step of any chaser below the look lights on its own,
    with the merged reach of every function below that starts no chaser."""
    below = graph.descendants(function_id)
    chasers = {member for member in below if graph.kind(member) == "Chaser"}
    shown: set[str] = set()
    for member in below:
        if not chasers & graph.descendants(member):
            shown.update(reach_swatches(graph, groups, member))
    return shown


def test_2026_10_19_a_wheel_tile_shows_its_steps_in_order_not_their_merged_max(shown):
    graph, groups, controls = shown
    for key in WHEELS:
        control = controls[key]
        assert control["functionType"] == "Chaser"
        steps = _step_colours(graph, groups, control["function"])
        assert len(steps) > 1, key
        assert control["swatches"] == steps[:MAX_SWATCHES], key
        assert control["swatches"] != ["#ffffff"], key


def test_2026_10_19_a_collection_over_wheels_shows_only_colours_a_step_shows(shown):
    graph, groups, controls = shown
    for key in OVER_WHEELS:
        control = controls[key]
        assert control["functionType"] == "Collection", key
        tile = control["swatches"]
        assert len(tile) > 1, key
        assert set(tile) <= _colours_any_step_shows(graph, groups, control["function"]), key


def test_2026_10_19_the_mix_wheel_tile_is_its_first_wheels_steps(shown):
    graph, groups, controls = shown
    mezcla = controls["mezcla"]["function"]
    first_wheel = graph.members[mezcla][0]
    assert graph.kind(first_wheel) == "Chaser"
    steps = _step_colours(graph, groups, first_wheel)
    assert controls["mezcla"]["swatches"] == steps[:MAX_SWATCHES]
    assert "#ffffff" not in controls["mezcla"]["swatches"]


def test_2026_10_19_the_merged_reach_would_draw_a_colour_no_step_shows(shown):
    """The bug put back: reading the merged reach of a wheel, or of a
    Collection over wheels, gives the tile a colour outside every step, which
    is what the tests above refuse."""
    graph, groups, controls = shown
    for key in ("pastel-tenue", "mezcla"):
        function_id = controls[key]["function"]
        merged = reach_swatches(graph, groups, function_id)
        assert set(merged) - _colours_any_step_shows(graph, groups, function_id), key
