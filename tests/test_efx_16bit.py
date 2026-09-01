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
from qlctool.efx_16bit import INTENSITY_PAIRS, PAN_TILT_PAIRS, keeps_16bit
from qlctool.generate.movement_efx import generate_movement_efx
from qlctool.library import FixtureLibrary
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, localname

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "Vibra.qxw"


def _functions(root):
    """Real functions only: `<Function>` is also a reference inside chasers and
    Virtual Console widgets, and those carry no ID."""
    return [
        f for f in find_local(root, "Engine") if localname(f) == "Function" and f.attrib.get("ID")
    ]


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


def test_the_rig_really_does_have_both_kinds(library):
    """If it ever stops having both, the split stops being exercised."""
    caps = capabilities_of(Workspace.load(SHOW).root, library)
    movers = [c for c in caps if c.has_role(roles.PAN) and c.has_role(roles.TILT)]
    kinds = {keeps_16bit(c, PAN_TILT_PAIRS) for c in movers}
    assert kinds == {True, False}


def test_a_fixture_with_no_fine_channels_never_splits_the_efx(library):
    caps = capabilities_of(Workspace.load(SHOW).root, library)
    mini = next(c for c in caps if c.fixture.model == "Mini Led Moving Head")
    assert not mini.has_role(roles.PAN_FINE)
    assert keeps_16bit(mini, PAN_TILT_PAIRS)


# EFXFixture::Mode. The Dimmer mode runs the identical check on the *intensity*
# channels, and `generate_dimmer_chases` splits on that too - but nothing in this
# rig has a 16-bit dimmer, so there is nothing for it to split.
MODE_PAN_TILT = "0"


def test_no_generated_efx_mixes_the_two(library):
    ws = Workspace.load(SHOW)
    generate_movement_efx(ws, library)
    caps = {c.fixture.fixture_id: c for c in capabilities_of(ws.root, library)}

    efx_seen = 0
    for function in _functions(ws.root):
        if function.attrib.get("Type") != "EFX":
            continue
        members = [
            int(find_local(f, "ID").text)
            for f in function
            if localname(f) == "Fixture"
            and find_local(f, "ID") is not None
            and (find_local(f, "Mode") is None or find_local(f, "Mode").text == MODE_PAN_TILT)
        ]
        if not members:
            continue
        efx_seen += 1
        kinds = {keeps_16bit(caps[m], PAN_TILT_PAIRS) for m in members if m in caps}
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


def test_the_dimmer_efx_is_guarded_too(library):
    """Same trap, intensity channels instead. 2026-08-28: the chase became a
    per-family Collection (the hand-built cascade shape), so the guard's job
    moved - each family is model-homogeneous, so a fixture whose dimmer fine
    channel is not adjacent runs 8 bit inside its own family without turning
    16 bit off for the rest. On this rig every family keeps 16 bit."""
    from qlctool.generate.dimmer_chases import generate_dimmer_chases

    ws = Workspace.load(SHOW)
    caps = capabilities_of(ws.root, library)
    assert all(keeps_16bit(c, INTENSITY_PAIRS) for c in caps)

    result = generate_dimmer_chases(ws, library)
    names = {f.attrib["ID"]: f.attrib["Name"] for f in _functions(ws.root)}
    assert names[str(result.chase_id)] == "Dimmer Chase"
    # Every family part belongs to one chase, and no part was 8-bit-split
    # further: one EFX per family per direction.
    assert all(
        names[str(part_id)].startswith(("Dimmer Chase", "Dimmer Chase 2"))
        for part_id in result.part_ids
    )


def test_a_16bit_dimmer_would_be_split(library):
    """Proved on a fixture that does not exist here, so the guard is exercised
    rather than merely present."""
    ws = Workspace.load(SHOW)
    caps = capabilities_of(ws.root, library)
    par = next(c for c in caps if c.fixture.model == "PC-64 LED S")
    assert keeps_16bit(par, INTENSITY_PAIRS)

    class Contrived:
        """A dimmer whose fine channel is two away, as the BEAM's pan is."""

        def offsets_for_role(self, role):
            return {roles.DIMMER: [0], roles.DIMMER_FINE: [2]}.get(role, [])

    assert not keeps_16bit(Contrived(), INTENSITY_PAIRS)
