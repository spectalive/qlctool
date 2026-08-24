"""Headless QLC+ validation: the real application must accept what we write.

Skipped where QLC+ is not installed - the toolkit still has its semantic
round-trip net there, but this stronger check needs the actual binary.
"""

from pathlib import Path

import pytest

from qlctool.generate.matrix_effects import generate_matrix_effects
from qlctool.generate.movement_efx import generate_movement_efx
from qlctool.library import FixtureLibrary
from qlctool.validate import qlcplus_binary, validate_workspace
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
