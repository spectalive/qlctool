"""The written plot: the rig as it is actually built, applied verbatim.

The generated band layout is a readable guess. This is not - somebody stood in
the venue and wrote down what hangs where, so the only job is to put it in
without improving it, and to refuse loudly when the plot no longer matches the
patch it was written against.
"""

import json
from pathlib import Path

import pytest

from qlctool.generate.stage_plot_layout import apply_stage_plot
from qlctool.monitor_node import POINTS_OF_VIEW
from qlctool.library import FixtureLibrary
from qlctool.stage_plot import load_stage_plot
from qlctool.fixture import patched_fixtures
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local

REPO = Path(__file__).resolve().parents[3]
# The plot is bound to the patch it describes, and the patch grew past the
# hand-built original when the other two pixel panels were added: Vibra.qxw is
# the current rig, DeluxeEventos2.qxw is kept as the reference the builders are
# tested against.
SHOW = REPO / "QLC+ Setups" / "Vibra.qxw"
PLOT = REPO / "QLC+ Setups" / "vibra-stage-plot.json"


@pytest.fixture
def workspace():
    return Workspace.load(SHOW)


def _depths(root):
    library = FixtureLibrary.load()
    return {
        f.fixture_id: next(
            d for (_, model), d in library._by_key.items() if model == f.model
        ).dimensions.depth
        for f in patched_fixtures(root)
    }


def _row(plot, depths, prefix):
    """Items whose place starts with `prefix`, left to right."""
    return sorted(
        (i for i in plot.items if plot.places[i.fixture_id].startswith(prefix)),
        key=lambda i: i.x,
    )


def test_the_standard_plot_matches_the_patch(workspace):
    plot = load_stage_plot(PLOT, workspace.root)
    assert len(plot.items) == 34
    # 10 on the back truss, 7 on the front truss, 2 beams beside the DJ table,
    # 1 bar over the booth, 1 smoke machine, 4 vertical fog machines on the
    # floor.
    assert len(plot.rigged) == 25
    # 2026-08-29: the two CromoWash that hung at back truss 4 and 7 did not
    # come to the show, and two Mac Mah MAC WASH 1915Z took their place. They
    # stay patched, so they park with the other spares.
    assert len(plot.spare) == 9


def test_the_front_truss_reads_left_to_right(workspace):
    plot = load_stage_plot(PLOT, workspace.root)
    front = _row(plot, _depths(workspace.root), "Front truss")
    # grid, pixel, pixel, bar, pixel, pixel, grid - the bar dead centre.
    assert [item.fixture_id for item in front] == [4, 24, 25, 2, 27, 28, 5]


def test_the_dj_beams_stand_on_their_flightcases_aimed_up(workspace):
    plot = load_stage_plot(PLOT, workspace.root)
    beams = [item for item in plot.items if item.fixture_id in (22, 23)]
    assert len(beams) == 2
    cases = [p for p in plot.props if "Flightcase" in p.name]
    assert len(cases) == 2
    case_top = cases[0].centre[1] + cases[0].size[1] / 2
    for beam in beams:
        assert beam.y == case_top
        assert beam.x_rot == 180


def test_the_audience_is_at_large_z(workspace):
    """QLC+'s 3D camera starts at +Z looking at -Z, so the front of the stage is
    the *high* z. Getting this backwards mirrors the whole rig, which is exactly
    what happened once."""
    plot = load_stage_plot(PLOT, workspace.root)
    by_place = {plot.places[i.fixture_id]: i for i in plot.items}
    back = next(i for p, i in by_place.items() if p.startswith("Back truss"))
    front = next(i for p, i in by_place.items() if p.startswith("Front truss"))
    assert front.z > back.z


def test_nothing_that_should_light_the_room_is_aimed_at_the_back_wall(workspace):
    """The sign that aims a fixture at the audience is not the same for all of
    them. QLC+ turns a fixture by *minus* the stored angle, and a meshed fixture
    emits down while one QLC+ draws itself - the pixel panels, the LED bars -
    emits from its top face. So a PAR leans out at +50 and a pixel bar faces the
    room at -90. This test asserted one uniform sign until 2026-08-25, and got
    it wrong in both directions on the same day."""
    plot = load_stage_plot(PLOT, workspace.root)
    aim = {i.fixture_id: i.x_rot for i in plot.items}

    for par in (6, 7, 8, 9, 10, 11):
        assert 0 < aim[par] < 90, "a truss PAR leans out, it does not point flat"
        assert aim[par] >= 50, "and far enough to clear the DJ"
    for out in (24, 25, 27, 28, 2, 3):
        assert aim[out] == -90, "panels and bars face the room"
    for grid in (4, 5):
        assert aim[grid] < 0, "the downstage grids look back at the stage"
    for beam in (22, 23):
        assert aim[beam] == 180, "the floor beams stand upright"


def test_the_booth_stands_on_the_floor(workspace):
    plot = load_stage_plot(PLOT, workspace.root)
    assert plot.props
    for prop in plot.props:
        bottom = prop.centre[1] - prop.size[1] / 2
        assert bottom >= -1, f"{prop.name} starts below the floor at {bottom}"


def test_the_back_truss_reads_left_to_right(workspace):
    plot = load_stage_plot(PLOT, workspace.root)
    truss = _row(plot, _depths(workspace.root), "Back truss")
    assert len(truss) == 10
    # LED PAR, beam, LED PAR, wash, LED PAR, LED PAR, wash, LED PAR, beam, LED PAR
    # The two washes are the MAC WASH 1915Z since 2026-08-29; the CromoWash
    # they replaced are patched but parked.
    assert [item.fixture_id for item in truss] == [
        6, 20, 7, 33, 8, 9, 34, 10, 21, 11
    ]


def test_nothing_hangs_off_the_edge_of_the_stage(workspace):
    plot = load_stage_plot(PLOT, workspace.root)
    width, height, depth = plot.stage
    for item in plot.items:
        assert 0 <= item.x <= width * 1000
        assert 0 <= item.y <= height * 1000
        assert 0 <= item.z <= depth * 1000


def test_no_two_rigged_fixtures_share_a_spot(workspace):
    plot = load_stage_plot(PLOT, workspace.root)
    spots = [
        (item.x, item.y, item.z) for item in plot.items if not item.hidden
    ]
    assert len(set(spots)) == len(spots)


def test_applying_it_writes_the_hidden_flag(workspace):
    plot = apply_stage_plot(workspace, load_stage_plot(PLOT, workspace.root))
    monitor = find_local(workspace.engine, "Monitor")
    items = {int(i.attrib["ID"]): i for i in findall_local(monitor, "FxItem")}
    assert set(items) == {item.fixture_id for item in plot.items}
    hidden = {fid for fid, i in items.items() if "Hidden" in i.attrib}
    assert hidden == set(plot.spare)

    grid = find_local(monitor, "Grid")
    assert grid.attrib["POV"] == str(POINTS_OF_VIEW["front"])


def test_a_stale_plot_is_refused(workspace, tmp_path):
    """A plot is bound to a patch - re-address or unpatch anything and the IDs
    move under it. Hanging a beam where a smoke machine is would be worse than
    stopping."""
    document = json.loads(PLOT.read_text())
    document["fixtures"][0]["model"] = "Something Else"
    stale = tmp_path / "stale.json"
    stale.write_text(json.dumps(document))

    with pytest.raises(ValueError, match="stale"):
        load_stage_plot(stale, workspace.root)


def test_a_plot_that_forgets_a_fixture_is_refused(workspace, tmp_path):
    document = json.loads(PLOT.read_text())
    dropped = document["fixtures"].pop()
    short = tmp_path / "short.json"
    short.write_text(json.dumps(document))

    with pytest.raises(ValueError, match="does not place"):
        load_stage_plot(short, workspace.root)


def test_a_plot_naming_an_unpatched_fixture_is_refused(workspace, tmp_path):
    document = json.loads(PLOT.read_text())
    document["fixtures"].append(
        {"id": 99, "model": "Ghost", "x": 0, "y": 0, "z": 0}
    )
    ghost = tmp_path / "ghost.json"
    ghost.write_text(json.dumps(document))

    with pytest.raises(ValueError, match="not patched"):
        load_stage_plot(ghost, workspace.root)


def test_every_row_has_its_fixtures_centred_on_one_line(workspace):
    """A stored position is a near corner, so fixtures of different depths on the
    same truss are only really in line once each is offset by half its own size.
    The depth flip that mirrored corners rather than centres is what this guards
    against."""
    plot = load_stage_plot(PLOT, workspace.root)
    depths = _depths(workspace.root)
    for prefix in ("Back truss", "Front truss", "On a flightcase", "Spare"):
        row = _row(plot, depths, prefix)
        assert row, prefix
        centres = [item.z + depths[item.fixture_id] / 2 for item in row]
        # Stored positions are whole millimetres, so a fixture of odd depth
        # lands half a millimetre off its line. Anything more is a real error.
        assert max(centres) - min(centres) <= 1, (
            f"{prefix!r} is not on one line: {sorted(set(centres))}"
        )
