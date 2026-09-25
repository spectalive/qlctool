"""2026-09-25: `newshow` refuses a rig below the minimum with a message, not a traceback.

Plan C final review: pars only stopped at "no fixture in this workspace has
both pan and tilt" (`movement_families.py`), washes only at "no fixture in
this workspace has a dimmer" (`dimmer_chases.py`), both as tracebacks, and a
patch with no fixture group built a show `check` then flagged. The README's
minimum - a pan/tilt fixture with a dimmer, one fixture group - is now asked
before any generator runs. Each case is one small patch; no show is built.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from qlctool.cli import main
from qlctool.names.default_names import default_names

EMPTY = Path(__file__).resolve().parent / "data" / "empty-workspace.qxw"
PAR = "Vortex|PC-64 LED S|Default|0|{address}|Par {index}"
WASH = "Chauvet|MiN Wash|13 Channel|0|{address}|Wash {index}"
BEAM = "LED Beam|Mini Led Moving Head|16 Channels|0|{address}|Beam {index}"


def _patch(folder: Path, spec: str, count: int, width: int, grouped: bool) -> Path:
    """`count` fixtures of one spec, in one row group when `grouped`."""
    empty = folder / "empty.qxw"
    shutil.copy(EMPTY, empty)
    adds = []
    for index in range(1, count + 1):
        adds += ["--add", spec.format(address=1 + (index - 1) * width, index=index)]
    groups = ["--group-new", f"Row={count}x1"] if grouped else []
    out = folder / "patch.qxw"
    assert main(["patch", str(empty), *adds, *groups, "--out", str(out)]) == 0
    return out


def _refusal(patch: Path, capsys) -> str:
    """The message `newshow` exits with; no workspace is written."""
    out = patch.with_name("show.qxw")
    with pytest.raises(SystemExit) as refused:
        main(["newshow", str(patch), "--out", str(out)])
    assert isinstance(refused.value.code, str)  # printed to stderr, exit status 1
    assert "Traceback" not in capsys.readouterr().err
    assert not out.exists()
    return refused.value.code


def _expected(*missing: str) -> str:
    names = default_names()
    words = ", ".join(names.display(identifier) for identifier in missing)
    return names.render("rig_below_minimum", missing=words)


def test_2026_09_25_pars_only_is_refused(tmp_path, capsys):
    patch = _patch(tmp_path, PAR, 6, 5, grouped=True)
    assert _refusal(patch, capsys) == _expected("rig_needs_pan_tilt_dimmer")


def test_2026_09_25_washes_only_is_refused(tmp_path, capsys):
    patch = _patch(tmp_path, WASH, 2, 13, grouped=True)
    assert _refusal(patch, capsys) == _expected("rig_needs_pan_tilt_dimmer")


def test_2026_09_25_heads_with_no_group_are_refused(tmp_path, capsys):
    patch = _patch(tmp_path, BEAM, 2, 16, grouped=False)
    assert _refusal(patch, capsys) == _expected("rig_needs_fixture_group")


def test_2026_09_25_the_process_exits_non_zero_without_a_traceback(tmp_path):
    patch = _patch(tmp_path, PAR, 6, 5, grouped=False)
    run = subprocess.run(
        [sys.executable, "-m", "qlctool.cli", "newshow", str(patch)],
        capture_output=True,
        text=True,
        env=os.environ.copy(),
        check=False,
    )
    assert run.returncode == 1
    assert "Traceback" not in run.stderr
    assert _expected("rig_needs_pan_tilt_dimmer", "rig_needs_fixture_group") in run.stderr
