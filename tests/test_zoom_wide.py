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
from qlctool.zoom_wide import zoom_wide_pairs

REPO = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def caps():
    workspace = Workspace.load(REPO / "QLC+ Setups" / "Vibra-split.qxw")
    return capabilities_of(workspace.root, FixtureLibrary.load())


def _by_model(caps, model):
    return next(c for c in caps if c.fixture.model == model)


def test_the_mac_wash_zoom_opens_to_the_top_of_the_channel(caps):
    wash = _by_model(caps, "MAC WASH 1915Z")
    # 23 Channel mode: offset 5, "SmallToBig" - 255 is the 50 degree end.
    assert zoom_wide_pairs(wash) == [(5, 255)]


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
