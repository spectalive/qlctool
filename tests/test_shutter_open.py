"""A scene that means a fixture to be seen has to open its shutter, not only its
dimmer.

The four BEAM 230W 7R are shut at DMX 0 on their shutter channel whatever the
dimmer says, and the two MiN Wash keep their whole intensity on a shutter-style
channel with no dimmer role at all. Every generated scene left both dark. The
hand-built show did it by hand - "Luz ON Cabezas" sends 255 to the beams'
channel 6 and "Luz OFF Cabezas" sends 0 - which is the evidence that 0 really is
shut on the hardware, not just in the definition.
"""

from pathlib import Path

import pytest

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.generate.color_scene import color_scene_values
from qlctool.generate.wheel_scenes import generate_wheel_scenes
from qlctool.library import FixtureLibrary
from qlctool.shutter_open import shutter_open_pairs
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, localname

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"


@pytest.fixture(scope="module")
def rig():
    ws = Workspace.load(SHOW)
    return ws, capabilities_of(ws.root, FixtureLibrary.load())


def _by_model(caps, model):
    return next(c for c in caps if c.fixture.model == model)


def test_the_beam_shutter_opens_at_the_top_of_the_channel(rig):
    _, caps = rig
    beam = _by_model(caps, "BEAM 230W 7R")
    pairs = shutter_open_pairs(beam)
    assert len(pairs) == 1
    offset, value = pairs[0]
    assert offset == 5
    # 241-255 "Open", the range clear of "Closed" at the bottom - and the value
    # the hand-built show used.
    assert value >= 241


def test_a_wash_with_no_dimmer_still_gets_opened(rig):
    _, caps = rig
    wash = _by_model(caps, "MiN Wash")
    assert wash.offsets_for_role(roles.DIMMER) == []
    assert shutter_open_pairs(wash) == [(5, 247)]


def test_a_led_par_with_only_a_strobe_channel_is_left_alone(rig):
    _, caps = rig
    par = _by_model(caps, "PC-64 LED S")
    assert par.has_role(roles.STROBE)
    assert shutter_open_pairs(par) == []


def test_a_colour_scene_opens_the_shutters_it_lights(rig):
    _, caps = rig
    values = color_scene_values(caps, (255, 0, 0))
    wash = _by_model(caps, "MiN Wash")
    assert (5, 247) in values[wash.fixture.fixture_id]


def test_a_colour_scene_with_the_dimmers_left_alone_opens_nothing(rig):
    _, caps = rig
    values = color_scene_values(caps, (255, 0, 0), dimmer_full=False)
    wash = _by_model(caps, "MiN Wash")
    assert not any(offset == 5 for offset, _ in values[wash.fixture.fixture_id])


def test_a_gobo_scene_opens_the_beams(rig):
    ws = Workspace.load(SHOW)
    library = FixtureLibrary.load()
    result = generate_wheel_scenes(ws, library, role=roles.GOBO, label="Gobo")
    scenes = {
        f.attrib["ID"]: f
        for f in find_local(ws.root, "Engine")
        if localname(f) == "Function" and f.attrib.get("ID")
    }
    beams = [
        c.fixture.fixture_id
        for c in capabilities_of(ws.root, library)
        if c.has_role(roles.GOBO)
    ]
    assert len(beams) == 4
    for scene_id in result.scene_ids:
        for values in findall_local(scenes[str(scene_id)], "FixtureVal"):
            nums = [int(v) for v in (values.text or "").split(",")]
            pairs = dict(zip(nums[::2], nums[1::2]))
            assert 6 in pairs and pairs[6] == 255, "dimmer still has to come up"
            assert 5 in pairs and pairs[5] >= 241, "and the shutter has to open"
