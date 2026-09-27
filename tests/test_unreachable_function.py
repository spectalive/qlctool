"""2026-09-27: a built function that nothing on the console starts is a finding.

Vibra without its smoke machines carried the panels' vertical-smoke light
chaser with no button to start it (2026-09-25); this rule would have seen it.
"""

import copy
from pathlib import Path

import pytest
from rig_root import RIG_ROOT
from single_shape_rig import build_single_shape_patch

from qlctool.checks.rule_unreachable_function import RULE_ID, check_unreachable_functions
from qlctool.cli import main
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, iter_local

PARS = ("Vortex|PC-64 LED S|Default|0|{address}|Par {index}", 3, 5)


@pytest.fixture(scope="module")
def show(tmp_path_factory) -> Path:
    folder = tmp_path_factory.mktemp("pars")
    out = folder / "show.qxw"
    assert main(["newshow", str(build_single_shape_patch(folder, *PARS)), "--out", str(out)]) == 0
    return out


@pytest.mark.parametrize("name", ["Vibra-split.qxw", "Vibra-beats.qxw"])
def test_2026_09_27_every_function_of_the_shipped_show_is_reached(name):
    root = Workspace.load(RIG_ROOT / "QLC+ Setups" / name).root
    assert check_unreachable_functions(root) == []


def test_2026_09_27_every_function_of_a_generated_show_is_reached(show):
    assert check_unreachable_functions(Workspace.load(show).root) == []


def test_2026_09_27_a_function_nothing_names_is_a_warning(show):
    root = Workspace.load(show).root
    engine = find_local(root, "Engine")
    assert engine is not None
    scene = next(f for f in iter_local(engine, "Function") if f.get("Type") == "Scene")
    orphan = copy.deepcopy(scene)
    orphan.set("ID", "9999")
    orphan.set("Name", "Orphan")
    engine.append(orphan)
    findings = check_unreachable_functions(root)
    assert [(f.rule_id, f.severity, f.function, f.fields["kind"]) for f in findings] == [
        (RULE_ID, "warning", "Orphan", "Scene")
    ]


def test_2026_09_27_a_step_of_a_reached_chaser_is_reached(show):
    root = Workspace.load(show).root
    engine = find_local(root, "Engine")
    assert engine is not None
    chaser = next(f for f in iter_local(engine, "Function") if f.get("Type") == "Chaser")
    step = next(iter_local(chaser, "Step"))
    step_id = (step.text or "").strip()
    scene = next(f for f in iter_local(engine, "Function") if f.get("ID") == step_id)
    orphan = copy.deepcopy(scene)
    orphan.set("ID", "9999")
    orphan.set("Name", "Only a step")
    engine.append(orphan)
    step.text = "9999"
    assert [f.function for f in check_unreachable_functions(root)] == [scene.get("Name")] or (
        check_unreachable_functions(root) == []
    )
