"""C-1 (2026-09-27 final review): validate never finished a workspace saved
outside the Virtual Console view.

The QML build's end-of-load marker (`renderPage`, `qml_loaded_markers.py`)
is logged only once the Virtual Console page has rendered, which happens
only when the workspace's `CurrentWindow` names it. `Vibra-split.qxw` ships
with `CurrentWindow="IOMGR"`, so before the fix (`force_vc_window`,
`offline_workspace`) validation timed out on it every time - measured by the
controller at 92 s on the shipped file, against 3 s once `CurrentWindow` was
`VC`. The stand-in now plays the same rule the real QLC+ 5 does (only log the
marker for a workspace saved on VC), so this fails without the fix.
"""

from pathlib import Path

import pytest
from rig_root import RIG_ROOT
from stand_in_qlcplus import stand_in_qlcplus

from qlctool.validate import validate_workspace

SPLIT = RIG_ROOT / "QLC+ Setups" / "Vibra-split.qxw"


@pytest.fixture
def home(tmp_path, monkeypatch) -> Path:
    """A HOME with no QLC+ settings in it, so no saved I/O patch is found."""
    monkeypatch.setenv("HOME", str(tmp_path))
    return tmp_path


def test_2026_09_27_validate_finishes_a_workspace_saved_outside_vc(home):
    assert SPLIT.exists()
    result = validate_workspace(
        SPLIT, binary=str(stand_in_qlcplus(home, "qlcplus-qml")), timeout=5, quiet_period=0.5
    )
    assert result.ok, result.describe()
