"""2026-09-26, second review of round D6: QLC+ opens the I/O patches in its own settings at startup.

`InputOutputMap::loadDefaults` runs before any workspace is loaded, so an
offline copy cannot keep those patches shut; validation refuses to start
while any exist, naming the keys and never their values.
"""

import plistlib

import pytest
from stand_in_qlcplus import stand_in_qlcplus

from qlctool.refuse_saved_io import refuse_saved_io
from qlctool.saved_io_patches import INI, PLIST, saved_io_patches
from qlctool.validate import validate_workspace

SECRET = "DMX USB interface serial 12345"


def _plist(home, keys):
    path = home / PLIST
    path.parent.mkdir(parents=True)
    with path.open("wb") as handle:
        plistlib.dump(dict.fromkeys(keys, SECRET), handle)


def test_the_macos_settings_keys_are_found_by_name_only(tmp_path):
    _plist(tmp_path, ["outputmap.universe0.plugin", "inputmap.universe1.input", "ui.language"])
    found = saved_io_patches(tmp_path)
    assert [key.rsplit(": ", 1)[1] for key in found] == [
        "inputmap.universe1.input",
        "outputmap.universe0.plugin",
    ]
    assert SECRET not in " ".join(found)


def test_the_linux_settings_sections_are_found(tmp_path):
    ini = tmp_path / INI[0]
    ini.parent.mkdir(parents=True)
    ini.write_text(f"[outputmap]\nuniverse0\\plugin={SECRET}\n[workspace]\nrecent0=x\n")
    found = saved_io_patches(tmp_path)
    assert found == [f"{ini}: [outputmap]"]


def test_no_settings_means_nothing_to_refuse(tmp_path):
    assert saved_io_patches(tmp_path) == []
    _plist(tmp_path, ["workspace.recent0", "ui.language"])
    assert saved_io_patches(tmp_path) == []


def test_validation_refuses_before_qlcplus_starts(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("QLCTOOL_ALLOW_SAVED_IO", raising=False)
    monkeypatch.setenv("FAKE_QLC_READY", str(tmp_path / "ready"))
    _plist(tmp_path, [f"outputmap.universe{n}.plugin" for n in range(6)])
    binary = stand_in_qlcplus(tmp_path)
    workspace = tmp_path / "show.qxw"
    workspace.write_text('<Workspace xmlns="http://www.qlcplus.org/Workspace"/>')
    with pytest.raises(RuntimeError) as refused:
        validate_workspace(workspace, binary=str(binary))
    said = str(refused.value)
    assert "outputmap.universe0.plugin" in said and "and 2 more" in said
    assert "QLCTOOL_ALLOW_SAVED_IO=1" in said and SECRET not in said
    assert not (tmp_path / "ready").exists(), "QLC+ was never started"


def test_the_refusal_can_be_overridden_knowingly(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("QLCTOOL_ALLOW_SAVED_IO", raising=False)
    _plist(tmp_path, ["outputmap.universe0.plugin"])
    with pytest.raises(RuntimeError):
        refuse_saved_io()
    refuse_saved_io(allowed=True)
    monkeypatch.setenv("QLCTOOL_ALLOW_SAVED_IO", "1")
    refuse_saved_io()
