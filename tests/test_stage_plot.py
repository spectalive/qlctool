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
from qlctool.stage_plot import load_stage_plot
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


def test_the_standard_plot_matches_the_patch(workspace):
    plot = load_stage_plot(PLOT, workspace.root)
    assert len(plot.items) == 29
    # 10 on the back truss, 7 on the front truss, 2 beams beside the DJ table,
    # 1 bar over the booth, 1 smoke machine.
    assert len(plot.rigged) == 21
    assert len(plot.spare) == 8


def test_the_front_truss_reads_left_to_right(workspace):
    plot = load_stage_plot(PLOT, workspace.root)
    front = sorted(
        (item for item in plot.items if item.y == 3000 and item.z == 1200),
        key=lambda item: item.x,
    )
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


def test_everything_that_faces_the_audience_is_turned_to_face_it(workspace):
    """0 is straight down, which is how QLC+'s meshes and its bars start. The
    truss PARs, the pixel panels and both LED bars all point out instead."""
    plot = load_stage_plot(PLOT, workspace.root)
    facing = {item.fixture_id for item in plot.items if item.x_rot == 90}
    pars = {6, 7, 8, 9, 10, 11}
    pixels = {24, 25, 27, 28}
    bars = {2, 3}
    assert facing == pars | pixels | bars


def test_the_booth_stands_on_the_floor(workspace):
    plot = load_stage_plot(PLOT, workspace.root)
    assert plot.props
    for prop in plot.props:
        bottom = prop.centre[1] - prop.size[1] / 2
        assert bottom >= -1, f"{prop.name} starts below the floor at {bottom}"


def test_the_back_truss_reads_left_to_right(workspace):
    plot = load_stage_plot(PLOT, workspace.root)
    truss = sorted(
        (item for item in plot.items if item.y == 4000 and item.z == 6500),
        key=lambda item: item.x,
    )
    assert len(truss) == 10
    # LED PAR, beam, LED PAR, wash, LED PAR, LED PAR, wash, LED PAR, beam, LED PAR
    assert [item.fixture_id for item in truss] == [
        6, 20, 7, 0, 8, 9, 1, 10, 21, 11
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
