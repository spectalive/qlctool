"""2026-09-26, round G: validation's two parked reads (second review of round D6).

After the kill, what was left of QLC+'s log was read with `readlines()`,
which waits for every holder of the pipe to close it, and a partial line
blocked `readline()` past the timeout; a QLC+ 5 load that timed out without
its end-of-load marker passed. A stand-in QLC+ plays each case.
"""

import os
import signal
import time
from pathlib import Path

import pytest
from rig_root import RIG_ROOT
from stand_in_qlcplus import stand_in_qlcplus

from qlctool.validate import validate_workspace

VIBRA = RIG_ROOT / "QLC+ Setups" / "Vibra.qxw"


@pytest.fixture
def home(tmp_path, monkeypatch) -> Path:
    """A HOME with no QLC+ settings in it, so no saved I/O patch is found."""
    monkeypatch.setenv("HOME", str(tmp_path))
    return tmp_path


def _pid_in(path: Path, within: float = 20) -> int:
    deadline = time.monotonic() + within
    while not path.exists():
        assert time.monotonic() < deadline, "the stand-in never wrote it"
        time.sleep(0.05)
    return int(path.read_text().strip())


@pytest.mark.parametrize("name", ["qlcplus", "qlcplus-qml"])
def test_2026_09_26_a_process_holding_the_log_open_does_not_hang_validation(
    home, monkeypatch, name
):
    """A detached `sleep` inherits the pipe for 60 s; validation returns in seconds."""
    orphan = home / "orphan"
    monkeypatch.setenv("FAKE_QLC_ORPHAN", str(orphan))
    binary = stand_in_qlcplus(home, name)
    started = time.monotonic()
    try:
        result = validate_workspace(VIBRA, binary=str(binary), timeout=10, quiet_period=0.5)
        elapsed = time.monotonic() - started
    finally:
        # Ours: the stand-in wrote this exact pid.
        os.kill(_pid_in(orphan), signal.SIGKILL)
    assert result.ok
    assert elapsed < 12


def test_2026_09_26_a_line_with_no_newline_does_not_block_past_the_timeout(home, monkeypatch):
    monkeypatch.setenv("FAKE_QLC_PARTIAL", "1")
    monkeypatch.setenv("FAKE_QLC_NO_MARKER", "1")
    started = time.monotonic()
    result = validate_workspace(VIBRA, binary=str(stand_in_qlcplus(home, "qlcplus-qml")), timeout=2)
    assert time.monotonic() - started < 6
    assert "a line that never ends" in result.log


def test_2026_09_26_a_qml_load_with_no_end_of_load_marker_fails(home, monkeypatch):
    monkeypatch.setenv("FAKE_QLC_NO_MARKER", "1")
    result = validate_workspace(VIBRA, binary=str(stand_in_qlcplus(home, "qlcplus-qml")), timeout=2)
    assert not result.ok
    assert result.errors[0].startswith("QLC+ never finished loading")
    assert "stand-in" in result.log, "the banner was printed: this used to pass"
