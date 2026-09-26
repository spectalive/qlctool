"""2026-09-26, reviews of round D6: validation touches only the QLC+ it started, on a copy with no I/O.

It used to hand QLC+ the workspace as it was - its DMX interface, Art-Net and
MIDI patches included - and to kill every QLC+ that appeared while it ran,
found by name. A stand-in QLC+ (`stand_in_qlcplus.py`, under both builds'
names) shows what it is given and when it runs, so this holds where no QLC+
is installed.
"""

import os
import subprocess
import threading
import time
from pathlib import Path

import pytest
from lxml import etree
from rig_root import RIG_ROOT
from stand_in_qlcplus import stand_in_qlcplus

from qlctool import validate
from qlctool.validate import validate_workspace
from qlctool.xmlutil import iter_local

VIBRA = RIG_ROOT / "QLC+ Setups" / "Vibra.qxw"
BUILDS = ("qlcplus", "qlcplus-qml")


@pytest.fixture
def ready(tmp_path, monkeypatch):
    """Where the stand-in reports; a HOME with no QLC+ settings in it."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("FAKE_QLC_SEEN", str(tmp_path / "seen.qxw"))
    monkeypatch.setenv("FAKE_QLC_READY", str(tmp_path / "ready"))
    return tmp_path / "ready"


def _report(ready: Path, within: float = 20) -> list[str]:
    deadline = time.monotonic() + within
    while not ready.exists():
        assert time.monotonic() < deadline, "the stand-in never started"
        time.sleep(0.05)
    return ready.read_text().splitlines()


def _gone(pid: int, within: float = 5) -> bool:
    deadline = time.monotonic() + within
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(0.05)
    return False


@pytest.mark.parametrize("name", BUILDS)
def test_qlcplus_is_given_a_copy_with_no_io(tmp_path, ready, name):
    binary = stand_in_qlcplus(tmp_path, name)
    assert validate_workspace(VIBRA, binary=str(binary), quiet_period=0.5).ok
    seen = etree.parse(str(tmp_path / "seen.qxw")).getroot()
    assert list(iter_local(seen, "Universe"))
    assert list(iter_local(etree.parse(str(VIBRA)).getroot(), "Output")), "a patch to strip"
    for io_map in iter_local(seen, "InputOutputMap"):
        assert not [e for n in ("Input", "Output", "Feedback") for e in iter_local(io_map, n)]
    pid, _, given = _report(ready)
    assert Path(given).parent == VIBRA.parent, "beside the original, so relative media resolve"
    assert not Path(given).exists(), "and removed afterwards"
    assert _gone(int(pid))


@pytest.mark.parametrize("name", BUILDS)
def test_a_qlcplus_started_during_a_validation_survives_it(tmp_path, ready, name):
    binary = stand_in_qlcplus(tmp_path, name)
    results = []
    validation = threading.Thread(
        target=lambda: results.append(validate_workspace(VIBRA, binary=str(binary), quiet_period=3))
    )
    validation.start()
    own = int(_report(ready)[0])
    # Somebody else's QLC+, same name, started while validation watches its own.
    other = subprocess.Popen([str(binary)], stdout=subprocess.DEVNULL)
    try:
        validation.join(30)
        assert results and results[0].ok
        assert _gone(own), "validation stops the QLC+ it started"
        assert other.poll() is None, "and nothing else"
    finally:
        other.kill()
        other.wait()


def test_a_child_of_the_qlcplus_it_started_is_stopped_too(tmp_path, ready, monkeypatch):
    """A wrapper that starts the real QLC+ under it: found by parent pid, never by name."""
    monkeypatch.setenv("FAKE_QLC_CHILD", "1")
    binary = stand_in_qlcplus(tmp_path)
    assert validate_workspace(VIBRA, binary=str(binary), quiet_period=0.5).ok
    pid, child, _ = _report(ready)
    assert int(child) and _gone(int(child)) and _gone(int(pid))


def test_the_qlcplus_it_started_is_stopped_when_reading_its_log_fails(tmp_path, ready, monkeypatch):
    def broken(*_args):
        _report(ready)
        raise OSError("the log pipe broke")

    monkeypatch.setattr(validate, "read_until_loaded", broken)
    with pytest.raises(OSError, match="log pipe"):
        validate_workspace(VIBRA, binary=str(stand_in_qlcplus(tmp_path)))
    assert _gone(int(_report(ready)[0]))


def test_a_truncated_workspace_is_refused_before_qlcplus_starts(tmp_path, ready):
    """QLC+ would load a truncated file up to the break, its I/O patches
    included, so it is never handed one (2026-09-26)."""
    broken = tmp_path / "broken.qxw"
    broken.write_bytes(VIBRA.read_bytes()[:4000])
    result = validate_workspace(broken, binary=str(stand_in_qlcplus(tmp_path)))
    assert not result.ok
    assert any("not well-formed XML" in error for error in result.errors)
    assert not ready.exists(), "QLC+ was never started"
