"""Round G review, 2026-09-26: page 4's help may name only the frames its page draws.

No fixture capability shows the mixes or the matrices frame, so the
caption-promise rule could not hold the help to the console; this rule reads
the console itself.
"""

from pathlib import Path

import pytest
from rig_root import RIG_ROOT
from single_shape_rig import build_single_shape_patch

from qlctool.checks.rule_help_names_frame import RULE_ID, check_help_names_frame
from qlctool.cli import main
from qlctool.names.default_names import default_names
from qlctool.names.frame_caption_head import frame_caption_head
from qlctool.workspace import Workspace
from qlctool.xmlutil import iter_local

PARS = ("Vortex|PC-64 LED S|Default|0|{address}|Par {index}", 3, 5)


@pytest.fixture(scope="module")
def show(tmp_path_factory) -> Path:
    folder = tmp_path_factory.mktemp("pars")
    out = folder / "show.qxw"
    assert main(["newshow", str(build_single_shape_patch(folder, *PARS)), "--out", str(out)]) == 0
    return out


def _without_frame(root, identifier: str) -> None:
    head = frame_caption_head(default_names().display(identifier))
    frame = next(
        f
        for tag in ("Frame", "SoloFrame")
        for f in iter_local(root, tag)
        if frame_caption_head(f.get("Caption", "")) == head
    )
    parent = frame.getparent()
    assert parent is not None
    parent.remove(frame)


def test_2026_09_27_the_shipped_show_draws_every_frame_its_help_names():
    root = Workspace.load(RIG_ROOT / "QLC+ Setups" / "Vibra-split.qxw").root
    assert check_help_names_frame(root) == []


def test_2026_09_27_a_generated_show_draws_every_frame_its_help_names(show):
    assert check_help_names_frame(Workspace.load(show).root) == []


def test_2026_09_27_deleting_the_mixes_frame_leaves_two_help_lines_promising_it():
    root = Workspace.load(RIG_ROOT / "QLC+ Setups" / "Vibra-split.qxw").root
    _without_frame(root, "mixes_frame")
    findings = check_help_names_frame(root)
    assert [(f.rule_id, f.severity, f.fields["frame"].message_id) for f in findings] == [
        (RULE_ID, "error", "mixes_frame")
    ] * 2
    assert {f.function for f in findings} == {
        default_names().display("library_1"),
        default_names().display("library_5"),
    }


def test_2026_09_27_deleting_the_matrices_frame_is_seen_too():
    root = Workspace.load(RIG_ROOT / "QLC+ Setups" / "Vibra-split.qxw").root
    _without_frame(root, "matrices_frame")
    findings = check_help_names_frame(root)
    assert [f.fields["frame"].message_id for f in findings] == ["matrices_frame"] * 2
