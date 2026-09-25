"""2026-09-25: a rig with no gobo, prism or haze machine gets a show (ruling C2).

`newshow` stopped at the gobo wheel ("no fixture in this workspace has a gobo
channel"), then at the haze timer, then at AUTO's members: every generator
assumed Vibra's beams and fog.
"""

from pathlib import Path

import pytest
from small_rig import build_small_rig_patch

from qlctool.checks.rule_dangling_reference import check_dangling_references
from qlctool.checks.show_graph import build_show_graph
from qlctool.cli import main
from qlctool.workspace import Workspace
from qlctool.xmlutil import iter_local


@pytest.fixture(scope="module")
def club(tmp_path_factory) -> Path:
    folder = tmp_path_factory.mktemp("club")
    patch = build_small_rig_patch(folder)
    out = folder / "club.qxw"
    assert main(["newshow", str(patch), "--out", str(out)]) == 0
    return out


def test_the_show_is_built(club):
    functions = list(iter_local(Workspace.load(club).root, "Function"))
    assert len(functions) > 100


def test_nothing_is_generated_for_what_the_rig_lacks(club):
    names = {f.get("Name") for f in iter_local(Workspace.load(club).root, "Function")}
    assert "Humo Auto" not in names
    assert "Gobo Animacion" not in names
    assert "Prisma Animacion" not in names
    assert "AUTO" in names


def test_no_member_names_a_function_that_was_never_built(club):
    """Plan C preflight (D3): `Talk Light` asked for a beams' white this rig lacks.

    Not `">None<"`: a frame's `<FrameStyle>` and `<BackgroundImage>` say None
    on purpose. A step is where the missing member showed.
    """
    root = Workspace.load(club).root
    assert ">None</Step>" not in club.read_text(encoding="utf-8")
    assert not check_dangling_references(build_show_graph(root, []), root)
