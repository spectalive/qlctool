"""Headless QLC+ validation: the real application must accept what we write.

Skipped where QLC+ is not installed - the toolkit still has its semantic
round-trip net there, but this stronger check needs the actual binary.
"""

from concurrent.futures import ThreadPoolExecutor

import pytest
from rig_root import RIG_ROOT

from qlctool.generate.generate_matrix_effects import generate_matrix_effects
from qlctool.generate.movement_efx import generate_movement_efx
from qlctool.library import FixtureLibrary
from qlctool.validate import qlcplus_binary, validate_workspace
from qlctool.workspace import Workspace

REPO = RIG_ROOT
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"

needs_qlcplus = pytest.mark.skipif(
    qlcplus_binary() is None, reason="QLC+ is not installed on this machine"
)


@needs_qlcplus
def test_the_real_show_validates():
    result = validate_workspace(SHOW)
    assert result.ok, result.describe()


@needs_qlcplus
def test_a_workspace_qlcplus_cannot_build_is_rejected(tmp_path):
    workspace = Workspace.load(SHOW)
    fixture = next(
        e for e in workspace.root.iter("{*}Fixture") if e.find("{*}Channels") is not None
    )
    fixture.find("{*}Model").text = "No Such Model"
    broken = tmp_path / "unknown-model.qxw"
    workspace.save(broken)

    result = validate_workspace(broken)

    assert not result.ok
    assert any("Such-Model" in error for error in result.errors)


@needs_qlcplus
def test_generated_functions_load_in_qlcplus(tmp_path):
    ws = Workspace.load(SHOW)
    generate_matrix_effects(
        ws,
        group_id=0,
        algorithms=["Strobe", None],
        palette={"Rojo": (255, 0, 0)},
    )
    generate_movement_efx(ws, FixtureLibrary.load())
    out = tmp_path / "generated.qxw"
    ws.save(out)

    result = validate_workspace(out)

    assert result.ok, result.describe()


@needs_qlcplus
def test_two_validations_at_once_keep_their_own_verdicts(tmp_path):
    """2026-09-22, the suite goes parallel: when validation read QLC+'s shared
    -g log, two validations launched at the same moment truncated each other's
    log and a broken workspace validated on its neighbour's clean load. Each
    validation now reads its own child's stdout; this keeps it that way.
    """
    workspace = Workspace.load(SHOW)
    fixture = next(
        e for e in workspace.root.iter("{*}Fixture") if e.find("{*}Channels") is not None
    )
    fixture.find("{*}Model").text = "No Such Model"
    broken = tmp_path / "unknown-model.qxw"
    workspace.save(broken)

    with ThreadPoolExecutor(max_workers=2) as pool:
        good, bad = pool.map(validate_workspace, [SHOW, broken])

    assert good.ok, good.describe()
    assert not bad.ok
    assert any("Such-Model" in error for error in bad.errors)


def test_missing_binary_raises_rather_than_passing(monkeypatch):
    monkeypatch.setenv("QLCTOOL_QLCPLUS", "/nonexistent/qlcplus")
    with pytest.raises(FileNotFoundError):
        validate_workspace(SHOW)
