"""One EFX cannot hold both kinds of moving head.

`EFXFixture` caches its pan and tilt channels when an EFX starts and, if a fine
channel is not directly after its coarse one, calls
`fader->setHandleSecondary(false)`. That fader belongs to the **EFX**, so one
badly ordered fixture turns 16 bit off for everybody in it.

Measured on this rig: with the four BEAM 230W 7R (`Pan, Tilt, Pan fine, Tilt
fine`) sharing an EFX with the CromoWash100 (`Pan, Pan fine, Tilt, Tilt fine`),
the washes read pan=0 tilt=0 with only their fine channels moving - one 256th
of the range. Split into two EFX they read pan=30 tilt=30 and move properly,
with no change to the fixtures or to QLC+.
"""

from pathlib import Path

import pytest

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.generate.movement_efx import generate_movement_efx
from qlctool.library import FixtureLibrary
from qlctool.pan_tilt_pairing import pairs_16bit
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, localname

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "Vibra.qxw"


def _functions(root):
    """Real functions only: `<Function>` is also a reference inside chasers and
    Virtual Console widgets, and those carry no ID."""
    return [
        f for f in find_local(root, "Engine")
        if localname(f) == "Function" and f.attrib.get("ID")
    ]


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


def test_the_rig_really_does_have_both_kinds(library):
    """If it ever stops having both, the split stops being exercised."""
    caps = capabilities_of(Workspace.load(SHOW).root, library)
    movers = [c for c in caps if c.has_role(roles.PAN) and c.has_role(roles.TILT)]
    kinds = {pairs_16bit(c) for c in movers}
    assert kinds == {True, False}


def test_a_fixture_with_no_fine_channels_never_splits_the_efx(library):
    caps = capabilities_of(Workspace.load(SHOW).root, library)
    mini = next(c for c in caps if c.fixture.model == "Mini Led Moving Head")
    assert not mini.has_role(roles.PAN_FINE)
    assert pairs_16bit(mini)


# EFXFixture::Mode - the pan/tilt hazard is only in the first one. The Dimmer
# mode has the identical check on the *intensity* channels, but nothing in this
# rig has a 16-bit dimmer, so its EFX may hold anything.
MODE_PAN_TILT = "0"


def test_no_generated_efx_mixes_the_two(library):
    ws = Workspace.load(SHOW)
    generate_movement_efx(ws, library)
    caps = {
        c.fixture.fixture_id: c for c in capabilities_of(ws.root, library)
    }

    efx_seen = 0
    for function in _functions(ws.root):
        if function.attrib.get("Type") != "EFX":
            continue
        members = [
            int(find_local(f, "ID").text)
            for f in function
            if localname(f) == "Fixture"
            and find_local(f, "ID") is not None
            and (find_local(f, "Mode") is None
                 or find_local(f, "Mode").text == MODE_PAN_TILT)
        ]
        if not members:
            continue
        efx_seen += 1
        kinds = {pairs_16bit(caps[m]) for m in members if m in caps}
        assert len(kinds) == 1, (
            f"{function.attrib['Name']!r} mixes 16-bit and 8-bit movers, which "
            "leaves the 16-bit ones with their coarse channels stuck at zero"
        )
    assert efx_seen


def test_the_console_still_sees_one_function_per_shape(library):
    """The split is invisible from the front: a Collection runs both halves."""
    ws = Workspace.load(SHOW)
    result = generate_movement_efx(ws, library)
    assert len(result.efx_ids) == 7
    assert len(result.part_ids) == 14

    names = {f.attrib["ID"]: f.attrib["Name"] for f in _functions(ws.root)}
    for function_id in result.efx_ids:
        assert "(" not in names[str(function_id)]
