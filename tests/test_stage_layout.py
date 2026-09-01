"""Placing the rig in the 2D/3D views.

The failure this guards against is the one the show shipped with: `<Monitor>`
carrying four positions out of 27, so QLC+ drew the whole rig on top of one
fixture. Every patched fixture has to come out with a spot of its own, and the
point of view has to be stored - without it QLC+ asks for one on first open and
rewrites every position it finds.
"""

from pathlib import Path

import pytest

from qlctool.fixture import patched_fixtures
from qlctool.generate.stage_layout import (
    POINTS_OF_VIEW,
    generate_stage_layout,
    spread,
)
from qlctool.library import FixtureLibrary
from qlctool.stage_band import BARS, BEAMS, PARS, SMOKE, WASHES
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"


@pytest.fixture(scope="module")
def laid_out():
    ws = Workspace.load(SHOW)
    result = generate_stage_layout(ws, FixtureLibrary.load())
    return ws, result


def _items(ws):
    monitor = find_local(ws.engine, "Monitor")
    return {int(i.attrib["ID"]): i for i in findall_local(monitor, "FxItem")}


def test_every_patched_fixture_gets_a_position(laid_out):
    ws, result = laid_out
    expected = {f.fixture_id for f in patched_fixtures(ws.root)}
    assert set(_items(ws)) == expected
    assert result.placed == len(expected)


def test_no_two_fixtures_share_a_spot(laid_out):
    ws, _ = laid_out
    spots = [(i.attrib["XPos"], i.attrib["YPos"], i.attrib["ZPos"]) for i in _items(ws).values()]
    assert len(set(spots)) == len(spots)


def test_bands_hold_the_fixtures_their_capabilities_say(laid_out):
    _, result = laid_out
    # The rig: 4 BEAM 230W have a gobo wheel, the other eight movers do not,
    # two LED bars plus the two pixel panels - both declare an LED Bar type and
    # both lie flat, so the band is theirs too - two smoke machines, and the
    # rest are plain colour fixtures.
    assert len(result.rows[BEAMS]) == 4
    assert len(result.rows[WASHES]) == 8
    assert len(result.rows[BARS]) == 4
    assert len(result.rows[SMOKE]) == 2
    assert len(result.rows[PARS]) == 9


def test_a_row_shares_one_height_and_depth(laid_out):
    ws, result = laid_out
    items = _items(ws)
    for fixture_ids in result.rows.values():
        rows = {(items[fid].attrib["YPos"], items[fid].attrib["ZPos"]) for fid in fixture_ids}
        assert len(rows) == 1


def test_the_point_of_view_is_stored(laid_out):
    ws, _ = laid_out
    grid = find_local(find_local(ws.engine, "Monitor"), "Grid")
    assert grid.attrib["POV"] == str(POINTS_OF_VIEW["front"])
    assert grid.attrib["Units"] == "0"
    assert (grid.attrib["Width"], grid.attrib["Height"], grid.attrib["Depth"]) == ("12", "6", "8")


def test_positions_stay_inside_the_stage(laid_out):
    ws, result = laid_out
    width, height, depth = result.stage
    for item in _items(ws).values():
        assert 0 <= float(item.attrib["XPos"]) <= width * 1000
        assert 0 <= float(item.attrib["YPos"]) <= height * 1000
        assert 0 <= float(item.attrib["ZPos"]) <= depth * 1000


def test_the_dmx_monitor_settings_survive(laid_out):
    ws, _ = laid_out
    monitor = find_local(ws.engine, "Monitor")
    assert monitor.attrib["DisplayMode"] == "0"
    assert find_local(monitor, "Font").text == "Arial,12,-1,5,50,0,0,0,0,0"
    assert find_local(monitor, "ChannelStyle").text == "1"


def test_child_order_matches_what_qlcplus_writes(laid_out):
    ws, _ = laid_out
    from qlctool.xmlutil import localname

    monitor = find_local(ws.engine, "Monitor")
    order = [localname(c) for c in monitor]
    assert order[:5] == ["Font", "ChannelStyle", "ValueStyle", "Grid", "StageItem"]
    assert set(order[5:]) == {"FxItem"}


def test_running_it_twice_is_idempotent():
    library = FixtureLibrary.load()
    once = Workspace.load(SHOW)
    generate_stage_layout(once, library)
    twice = Workspace.load(SHOW)
    generate_stage_layout(twice, library)
    generate_stage_layout(twice, library)
    assert once.to_bytes() == twice.to_bytes()


def test_an_unknown_point_of_view_is_refused():
    ws = Workspace.load(SHOW)
    with pytest.raises(ValueError):
        generate_stage_layout(ws, FixtureLibrary.load(), point_of_view="above")


def test_spread_centres_a_single_fixture_and_clears_the_ends():
    assert spread(1, 12000, 960) == [6000]
    assert spread(2, 12000, 960) == [960, 11040]
    assert spread(0, 12000, 960) == []


def test_unplaced_fixtures_finds_the_gap():
    from qlctool.generate.stage_layout import unplaced_fixtures

    ws = Workspace.load(SHOW)
    # The show as shipped: four positions written by hand, the rest missing.
    missing = unplaced_fixtures(ws)
    assert len(missing) == len(patched_fixtures(ws.root)) - 4
    generate_stage_layout(ws, FixtureLibrary.load())
    assert unplaced_fixtures(ws) == []
