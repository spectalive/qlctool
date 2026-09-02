"""Which end of a zoom channel is the wide one, and who has one at all.

2026-08-29: the MAC WASH 1915Z is the first fixture in this rig whose beam width
is a DMX channel. The direction comes out of the definition's capability preset,
never out of a model name - a `BigToSmall` zoom driven to 255 is the narrowest
the head has, which is the bug this module exists to prevent.
"""

from pathlib import Path

import pytest

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.library import FixtureLibrary
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, localname
from qlctool.zoom_wide import zoom_wide_pairs

REPO = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def caps():
    workspace = Workspace.load(REPO / "QLC+ Setups" / "Vibra-split.qxw")
    return capabilities_of(workspace.root, FixtureLibrary.load())


def _by_model(caps, model):
    return next(c for c in caps if c.fixture.model == model)


def test_the_mac_wash_zoom_opens_to_the_bottom_of_the_channel(caps):
    """2026-09-02: this test said 255 for a week, and so did both washes.

    The manual prints `Zoom 000-255` and nothing else, the definition guessed
    `SmallToBig`, and every look ran the washes at 6 degrees. ChamSys MagicQ's
    personality for the unit says *Wide to Narrow 0-255*; the definition is
    `BigToSmall` now and the wide end is 0.
    """
    wash = _by_model(caps, "MAC WASH 1915Z")
    # 23 Channel mode: offset 5, "BigToSmall" - 0 is the 50 degree end.
    assert zoom_wide_pairs(wash) == [(5, 0)]


def test_a_fixture_with_no_zoom_is_left_alone(caps):
    cromo = _by_model(caps, "CromoWash100")
    assert not cromo.has_role(roles.ZOOM)
    assert zoom_wide_pairs(cromo) == []


def test_a_zoom_that_does_not_say_which_end_is_wide_is_left_alone(caps):
    """A guess here is a wash driven to its narrowest, so there is no guess."""
    from dataclasses import replace

    from qlctool.definition import Capability

    wash = _by_model(caps, "MAC WASH 1915Z")
    silent = list(wash.capabilities_by_offset)
    silent[5] = (Capability(minimum=0, maximum=255, name="Zoom"),)
    assert zoom_wide_pairs(replace(wash, capabilities_by_offset=silent)) == []


def test_the_matrix_base_scene_writes_zoom_too():
    """2026-08-31: the two MAC WASH joined a fixture group so they would get a
    colour bank and a matrix. `Pixeles ON` is what holds a matrix-lit fixture
    open - a matrix writes RGB and nothing else - and it wrote dimmer, shutter
    and strobe-off but not zoom.

    Every other scene that owns the light writes it. On a cold desk an
    unwritten zoom is 0, which on these heads is the narrowest beam they have,
    so the wash would have come up as a pencil. `qlctool check`'s
    `zoom sin declarar` reported it the moment the group existed.
    """
    workspace = Workspace.load(REPO / "QLC+ Setups" / "Vibra-split.qxw")
    library = FixtureLibrary.load()
    capabilities = capabilities_of(workspace.root, library)
    washes = [c for c in capabilities if zoom_wide_pairs(c) and "MAC WASH" in c.fixture.name]
    assert washes, "the MAC WASH lost their zoom channel; this test is stale"

    scene = next(
        function
        for function in find_local(workspace.root, "Engine")
        if localname(function) == "Function" and function.attrib.get("Name") == "Pixeles ON"
    )
    written = {
        int(value.attrib["ID"]): {int(n) for n in (value.text or "").split(",")[0::2]}
        for value in findall_local(scene, "FixtureVal")
    }

    for capability in washes:
        offsets = {offset for offset, _ in zoom_wide_pairs(capability)}
        assert offsets <= written.get(capability.fixture.fixture_id, set()), (
            f"{capability.fixture.name} is lit by Pixeles ON with no zoom"
        )
