"""Spec step 7 (2026-09-25): a second rig, described in English, with no controllers.

The example is regenerated from its description and must match the committed
file byte for byte, pass every check and load in QLC+ - the proof that a
description and a patch are enough, with nothing of Vibra's.
"""

import hashlib
from pathlib import Path

import pytest

from qlctool.checks.pad_bindings import pad_bindings
from qlctool.checks.rule_providers import rule_providers
from qlctool.checks.run import check_workspace
from qlctool.cli import main
from qlctool.desk_function_path import DESK_FUNCTION_PATH
from qlctool.library import FixtureLibrary
from qlctool.validate import qlcplus_binary, validate_workspace
from qlctool.workspace import Workspace

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "small-club"


@pytest.fixture(scope="module")
def regenerated(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("club") / "club.qxw"
    assert main(["newshow", "--description", str(EXAMPLE / "show.toml"), "--out", str(out)]) == 0
    return out


def test_the_example_regenerates_byte_for_byte(regenerated):
    digest = hashlib.sha256(regenerated.read_bytes()).hexdigest()
    assert digest == hashlib.sha256((EXAMPLE / "club.qxw").read_bytes()).hexdigest()


def test_the_example_passes_every_check(regenerated):
    library = FixtureLibrary.load([EXAMPLE / "fixtures"])
    assert check_workspace(Workspace.load(regenerated), library) == []


def test_the_example_has_no_controller(regenerated):
    """No pad binding, no desk function, no controller's rules: keyboard keys stay."""
    ws = Workspace.load(regenerated)
    assert not pad_bindings(ws.root)
    assert not any(f.get("Path") == DESK_FUNCTION_PATH for f in ws.engine)
    own = [p for p in rule_providers() if p.name in ("smc-pad", "tablet_desk")]
    assert not any(p.applies(ws.root) for p in own)
    assert "Desk · " not in regenerated.read_text(encoding="utf-8")


@pytest.mark.skipif(qlcplus_binary() is None, reason="QLC+ is not installed on this machine")
def test_qlcplus_loads_the_example(regenerated):
    assert validate_workspace(regenerated).errors == []
