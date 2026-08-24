"""Re-patch operations against the real show: address, rename, remove, add.

The patch is the layer where a mistake is invisible in the file and wrong on
stage, so every mutation here is checked against the whole patch afterwards and
every test round-trips through save/load.
"""

from pathlib import Path

import pytest

from qlctool.capabilities_of import capabilities_of
from qlctool.fixture import patched_fixtures
from qlctool.fixture_references import fixture_references
from qlctool.library import FixtureLibrary
from qlctool.patch_conflicts import patch_conflicts
from qlctool.repatch.add import add_fixture
from qlctool.repatch.address import set_fixture_address
from qlctool.repatch.patch_element import patch_element
from qlctool.repatch.remove import remove_fixture
from qlctool.repatch.rename import rename_fixture
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"
FREE_ADDRESS = 300  # 0-based; the show patches 0-299 contiguously


def _fixture(root, fixture_id):
    return next(
        f for f in patched_fixtures(root) if f.fixture_id == fixture_id
    )


def test_real_show_patch_is_clean():
    root = Workspace.load(SHOW).root
    assert patch_conflicts(root) == []
    assert len(patched_fixtures(root)) == 27


def test_overlap_is_detected_and_described():
    ws = Workspace.load(SHOW)
    introduced = set_fixture_address(ws.root, 1, 0, allow_overlap=True)

    assert introduced
    conflicts = patch_conflicts(ws.root)
    assert conflicts
    described = "; ".join(c.describe() for c in conflicts)
    assert "U0 channels 1-" in described


def test_set_address_rejects_an_overlap_and_rolls_back():
    ws = Workspace.load(SHOW)
    before = _fixture(ws.root, 1)

    with pytest.raises(ValueError, match="would overlap"):
        set_fixture_address(ws.root, 1, 0)

    assert _fixture(ws.root, 1).address == before.address
    assert patch_conflicts(ws.root) == []


def test_set_address_moves_and_survives_a_round_trip(tmp_path):
    ws = Workspace.load(SHOW)
    assert set_fixture_address(ws.root, 25, FREE_ADDRESS, universe=1) == []

    out = tmp_path / "out.qxw"
    ws.save(out)
    moved = _fixture(Workspace.load(out).root, 25)

    assert (moved.universe, moved.address) == (1, FREE_ADDRESS)
    assert patch_conflicts(Workspace.load(out).root) == []


def test_rename_touches_only_the_name(tmp_path):
    ws = Workspace.load(SHOW)
    before = _fixture(ws.root, 0)

    previous = rename_fixture(ws.root, 0, "Wash Frontal 1")

    assert previous == before.name
    out = tmp_path / "out.qxw"
    ws.save(out)
    after = _fixture(Workspace.load(out).root, 0)
    assert after.name == "Wash Frontal 1"
    assert (after.universe, after.address, after.channels) == (
        before.universe, before.address, before.channels
    )


def test_remove_clears_every_reference(tmp_path):
    ws = Workspace.load(SHOW)
    # Fixture 0 is referenced from scenes, an EFX and a Virtual Console XY pad.
    references_before = fixture_references(ws.root, 0)
    assert len(references_before) > 50

    removed = remove_fixture(ws.root, 0)
    assert removed == len(references_before)

    out = tmp_path / "out.qxw"
    ws.save(out)
    reloaded = Workspace.load(out).root

    assert fixture_references(reloaded, 0) == []
    assert len(patched_fixtures(reloaded)) == 26
    with pytest.raises(KeyError):
        patch_element(reloaded, 0)


def test_add_takes_its_channel_count_from_the_definition(tmp_path):
    ws = Workspace.load(SHOW)
    library = FixtureLibrary.load()

    fixture_id = add_fixture(
        ws.root, library, "Vortex", "PC-64 LED S", "Default",
        universe=0, address=FREE_ADDRESS, name="PAR Extra",
    )

    out = tmp_path / "out.qxw"
    ws.save(out)
    reloaded = Workspace.load(out).root

    added = _fixture(reloaded, fixture_id)
    assert (added.name, added.channels, added.address) == ("PAR Extra", 5, 300)
    assert patch_conflicts(reloaded) == []
    # The new entry is complete enough for the capability layer to resolve it.
    resolved = next(
        c for c in capabilities_of(reloaded, library)
        if c.fixture.fixture_id == fixture_id
    )
    assert "red" in resolved.roles


def test_add_rejects_unknown_model_mode_and_overlap():
    ws = Workspace.load(SHOW)
    library = FixtureLibrary.load()

    with pytest.raises(KeyError, match="no definition"):
        add_fixture(ws.root, library, "Nope", "Nothing", "Default", 0, FREE_ADDRESS)
    with pytest.raises(KeyError, match="no mode"):
        add_fixture(ws.root, library, "Vortex", "PC-64 LED S", "Nope", 0, FREE_ADDRESS)
    with pytest.raises(ValueError, match="would overlap"):
        add_fixture(ws.root, library, "Vortex", "PC-64 LED S", "Default", 0, 0)

    # Every rejection leaves the patch exactly as it was.
    assert len(patched_fixtures(ws.root)) == 27
    assert patch_conflicts(ws.root) == []
