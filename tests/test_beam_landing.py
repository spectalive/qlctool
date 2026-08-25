"""The plot is checked with arithmetic, not by squinting at the preview.

Aiming by eye is how the truss PARs came to sit at 35 degrees off vertical,
which from four metres up lands them at z=4485 - the DJ deck is at 4500. It read
as "tilted towards the audience" and it was, by two metres too few.
"""

import math
from pathlib import Path

import pytest

from qlctool.beam_landing import HANGING, STANDING, beam_landing
from qlctool.capabilities_of import capabilities_of
from qlctool.library import FixtureLibrary
from qlctool.stage_plot import load_stage_plot
from qlctool.workspace import Workspace

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "Vibra.qxw"
PLOT = REPO / "QLC+ Setups" / "vibra-stage-plot.json"

# The room, in the plot's own coordinates: depth grows towards the audience.
DJ_HEAD_TOP = 1715
DJ_Z = 3750
DECK_Z = 4500
STAGE_FRONT = 8000


@pytest.fixture(scope="module")
def rig():
    ws = Workspace.load(SHOW)
    plot = load_stage_plot(PLOT, ws.root)
    caps = {
        c.fixture.fixture_id: c
        for c in capabilities_of(ws.root, FixtureLibrary.load())
    }
    return plot, caps


def test_a_moving_head_is_mounted_never_aimed(rig):
    """Its rotation says how the body hangs; pan and tilt say where the light
    goes. Tilting the mounting only leaves it crooked on its clamp."""
    plot, caps = rig
    for item in plot.items:
        capability = caps.get(item.fixture_id)
        if capability is None:
            continue
        landing = beam_landing(item, capability)
        if "moving head" not in landing.reason:
            continue
        assert item.x_rot in (HANGING, STANDING), (
            f"fixture {item.fixture_id} is a mover mounted at {item.x_rot}"
        )


def test_the_truss_pars_pass_over_the_dj_and_reach_the_room(rig):
    plot, caps = rig
    pars = [
        item for item in plot.items
        if not item.hidden
        and caps[item.fixture_id].fixture.model == "PC-64 LED S"
    ]
    assert len(pars) == 6

    for par in pars:
        landing = beam_landing(par, caps[par.fixture_id])
        assert landing.z is not None
        assert landing.z > STAGE_FRONT, (
            f"fixture {par.fixture_id} lands at {landing.z:.0f}, short of the "
            "front of the stage"
        )
        # Height of the beam as it goes over him.
        drop = (DJ_Z - par.z) / math.tan(math.radians(-par.x_rot))
        assert par.y - drop > DJ_HEAD_TOP + 500, "it would be in the DJ's face"


def test_the_downstage_grids_land_on_the_dj(rig):
    plot, caps = rig
    for fixture_id in (4, 5):
        item = next(i for i in plot.items if i.fixture_id == fixture_id)
        landing = beam_landing(item, caps[fixture_id])
        assert landing.z is not None
        assert DJ_Z <= landing.z <= DECK_Z + 500


def test_what_faces_the_room_never_reaches_the_floor(rig):
    plot, caps = rig
    for fixture_id in (2, 3, 24, 25, 27, 28):
        item = next(i for i in plot.items if i.fixture_id == fixture_id)
        landing = beam_landing(item, caps[fixture_id])
        assert landing.z is None
        assert landing.reason == "aimed level or upward"


def test_a_smoke_machine_has_no_beam(rig):
    plot, caps = rig
    item = next(i for i in plot.items if i.fixture_id == 17)
    assert beam_landing(item, caps[17]).reason == "smoke machine: no beam"
