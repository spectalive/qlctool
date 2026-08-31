"""Headless QLC+ validation: the real application must accept what we write.

Skipped where QLC+ is not installed - the toolkit still has its semantic
round-trip net there, but this stronger check needs the actual binary.
"""

from pathlib import Path

import pytest

from qlctool.generate.matrix_effects import generate_matrix_effects
from qlctool.generate.movement_efx import generate_movement_efx
from qlctool.library import FixtureLibrary
from qlctool.validate import (
    current_session,
    qlcplus_binary,
    validate_workspace,
)
from qlctool.workspace import Workspace

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"

needs_qlcplus = pytest.mark.skipif(
    qlcplus_binary() is None, reason="QLC+ is not installed on this machine"
)


@needs_qlcplus
def test_the_real_show_validates():
    result = validate_workspace(SHOW)
    assert result.ok, result.describe()


@needs_qlcplus
def test_a_truncated_workspace_is_rejected(tmp_path):
    broken = tmp_path / "broken.qxw"
    broken.write_bytes(SHOW.read_bytes()[:4000])

    result = validate_workspace(broken)

    assert not result.ok
    assert any("cannot be created" in error for error in result.errors)


@needs_qlcplus
def test_generated_functions_load_in_qlcplus(tmp_path):
    ws = Workspace.load(SHOW)
    generate_matrix_effects(
        ws, group_id=0, algorithms=["Strobe", None],
        palette={"Rojo": (255, 0, 0)},
    )
    generate_movement_efx(ws, FixtureLibrary.load())
    out = tmp_path / "generated.qxw"
    ws.save(out)

    result = validate_workspace(out)

    assert result.ok, result.describe()


def test_missing_binary_raises_rather_than_passing(monkeypatch):
    monkeypatch.setenv("QLCTOOL_QLCPLUS", "/nonexistent/qlcplus")
    with pytest.raises(FileNotFoundError):
        validate_workspace(SHOW)


def test_a_dying_qlcplus_does_not_hand_its_errors_to_the_next_workspace():
    """2026-08-25: `test_qlcplus_loads_the_show` failed once under the full
    suite with "fixture 13 overlapping with fixture ...", while passing in
    isolation and on every re-run.

    QLC+'s -g log has one hard-coded name and is opened in append mode, so
    every validation shares it. Truncating before a launch does not help: the
    previous test's QLC+, still shutting down, keeps writing - and the
    neighbouring test that deliberately builds a broken workspace hands its
    complaint to whoever reads the file next. The verdict must only ever see
    the session this call started.
    """
    log = (
        "bool QLCFixtureDefCache::load(const QDir &) \"/x/Fixtures\"\n"
        "Fixture 13 overlapping with fixture 12\n"
        "bool QLCFixtureDefCache::load(const QDir &) \"/x/Fixtures\"\n"
        "1730 fixtures found in map\n"
        "renderPage\n"
    )

    session = current_session(log)

    assert "overlapping" not in session
    assert session.startswith("bool QLCFixtureDefCache::load")
    assert "renderPage" in session


def test_a_log_without_the_start_marker_keeps_every_line():
    """A build that logs something else must not silently drop a complaint."""
    log = "Fixture 13 overlapping with fixture 12\n"

    assert current_session(log) == log


def test_the_session_marker_is_not_the_line_after_it():
    """QLC+ logs `QLCFixtureDefCache::loadMap` immediately after
    `QLCFixtureDefCache::load`, so a prefix match takes the second line as the
    start of the session and drops the first (2026-08-31)."""
    log = (
        'bool QLCFixtureDefCache::load(const QDir &) "/x/Fixtures"\n'
        'bool QLCFixtureDefCache::loadMap(const QDir &) "/y/Fixtures"\n'
        "renderPage\n"
    )

    assert current_session(log) == log
