"""2026-09-25: a rig with no gobo, prism or haze machine gets a show (ruling C2).

`newshow` stopped at the gobo wheel ("no fixture in this workspace has a gobo
channel"), then at the haze timer, then at AUTO's members: every generator
assumed Vibra's beams and fog.
"""

from pathlib import Path

import pytest
from gobo_spot_rig import build_gobo_spot_patch
from small_rig import build_small_rig_patch

from qlctool.checks.rule_dangling_reference import check_dangling_references
from qlctool.checks.rule_empty_frame import check_empty_frames
from qlctool.checks.show_graph import build_show_graph
from qlctool.cli import main
from qlctool.names.default_names import default_names
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


def _captions(club: Path) -> list[str]:
    root = Workspace.load(club).root
    return [
        e.get("Caption") or "" for e in root.iter() if isinstance(e.tag, str) and e.get("Caption")
    ]


def test_no_frame_is_left_with_nothing_to_press(club):
    """Plan C preflight (D9): the haze row, and the gobo, prism and pixel families."""
    assert not check_empty_frames(Workspace.load(club).root)


def test_the_console_does_not_speak_of_haze(club):
    """Plan C preflight (D9): no haze machine, so no haze row, hit or help line."""
    haze = default_names().display("haze_word").casefold()
    assert not [c for c in _captions(club) if haze in c.casefold()]


def test_the_aim_label_names_no_count(club):
    """Plan C preflight (D9): the label said 12 heads on a rig with 4.

    Owner decision, 2026-09-25: the label carries no number on any rig.
    """
    aim = default_names().display("aim_frame")
    assert aim in _captions(club)
    assert not any(ch.isdigit() for ch in aim)


def test_the_control_page_does_not_promise_beam_wheels(club):
    """2026-09-25, Plan C Task 4: page 3 said "ruedas de BEAM" on this rig.

    Its heads mix RGB and have no colour wheel, so no beam wheel frame is
    built; the title names only what the page holds.
    """
    names = default_names()
    captions = _captions(club)
    assert names.display("page_control_no_haze_no_beam_wheel") in captions
    wheel_titles = [names.display(k) for k in ("page_control", "page_control_no_haze")]
    assert not [c for c in captions if c in wheel_titles]


def test_2026_09_25_the_tempo_help_names_no_gobo_or_prism(club):
    """2026-09-25, Plan C final review: page 1 said gobos and prism follow the tap.

    The LED Beam heads have no gobo or prism wheel, so neither animation is
    built and the dial re-times neither.
    """
    names = default_names()
    captions = _captions(club)
    assert names.display("tempo_2") not in captions
    assert not [c for c in captions if "gobo" in c.casefold() or "prism" in c.casefold()]


def test_2026_09_25_the_matrices_frame_names_no_bars_or_panels(club):
    """2026-09-25, Plan C final review: page 4 drew "patterns on the bars and panels".

    The club's matrices run on its pars and its heads: no fixture is made of
    pixels and none has built-in effects.
    """
    assert default_names().display("matrices_frame") not in _captions(club)


def test_2026_09_25_the_library_help_names_no_built_in_effects(club):
    """2026-09-25, Plan C final review: page 4 spoke of "the panels' 42 built-in effects".

    Nothing on this rig has built-in effects, so no panels frame is built and
    the help lines about it have nothing to point at.
    """
    names = default_names()
    captions = _captions(club)
    for key in ("library_1", "library_2", "library_6", "library_7"):
        assert names.display(key) not in captions, key
    assert not [c for c in captions if "panel" in c.casefold() or "42" in c]


def test_2026_09_25_a_gobo_spot_with_no_colour_wheel_gets_a_show(tmp_path, monkeypatch):
    """2026-09-25, Plan C final review: an LED gobo spot with no Color Macro.

    The beams' colour wheel was built for every fixture with a gobo, so
    `newshow` stopped at "no fixture in this workspace has a color_macro
    channel" on a rig whose gobo spots mix no wheel at all.
    """
    monkeypatch.setenv("QLCTOOL_FIXTURES", str(tmp_path / "fixtures"))
    patch = build_gobo_spot_patch(tmp_path)
    out = tmp_path / "spots.qxw"
    assert main(["newshow", str(patch), "--out", str(out)]) == 0
    assert main(["check", str(out)]) == 0
