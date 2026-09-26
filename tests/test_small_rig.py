"""2026-09-25: a rig with no gobo, prism or haze machine gets a show (ruling C2).

`newshow` stopped at the gobo wheel ("no fixture in this workspace has a gobo
channel"), then at the haze timer, then at AUTO's members: every generator
assumed Vibra's beams and fog.
"""

from pathlib import Path

import pytest
from console_captions import console_captions
from gobo_spot_rig import build_gobo_spot_patch
from single_shape_rig import build_single_shape_patch
from small_rig import build_small_rig_patch

from qlctool.capabilities_of import capabilities_of
from qlctool.checks.rule_caption_promise import check_caption_promise
from qlctool.checks.rule_dangling_reference import check_dangling_references
from qlctool.checks.rule_empty_frame import check_empty_frames
from qlctool.checks.show_graph import build_show_graph
from qlctool.cli import main
from qlctool.generate.library_help_lines import library_help_lines
from qlctool.generate.matrices_frame_caption import matrices_frame_caption
from qlctool.generate.page_control_title import page_control_title
from qlctool.generate.tempo_help_line import tempo_help_line
from qlctool.library import FixtureLibrary
from qlctool.names.default_names import default_names
from qlctool.validate import qlcplus_binary, validate_workspace
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


def test_no_frame_is_left_with_nothing_to_press(club):
    """Plan C preflight (D9): the haze row, and the gobo, prism and pixel families."""
    assert not check_empty_frames(Workspace.load(club).root)


def test_the_console_does_not_speak_of_haze(club):
    """Plan C preflight (D9): no haze machine, so no haze row, hit or help line."""
    haze = default_names().display("haze_word").casefold()
    assert not [c for c in console_captions(club) if haze in c.casefold()]


def test_the_aim_label_names_no_count(club):
    """Plan C preflight (D9): the label said 12 heads on a rig with 4.

    Owner decision, 2026-09-25: the label carries no number on any rig.
    """
    aim = default_names().display("aim_frame")
    assert aim in console_captions(club)
    assert not any(ch.isdigit() for ch in aim)


def test_the_control_page_does_not_promise_beam_wheels(club):
    """2026-09-25, Plan C Task 4: page 3 said "ruedas de BEAM" on this rig.

    Its heads mix RGB and have no colour wheel, so no beam wheel frame is
    built; the title names only what the page holds.
    """
    names = default_names()
    captions = console_captions(club)
    assert names.display("page_control_no_haze_no_beam_wheel") in captions
    wheel_titles = [names.display(k) for k in ("page_control", "page_control_no_haze")]
    assert not [c for c in captions if c in wheel_titles]


def test_2026_09_25_the_tempo_help_names_no_gobo_or_prism(club):
    """2026-09-25, Plan C final review: page 1 said gobos and prism follow the tap.

    The LED Beam heads have no gobo or prism wheel, so neither animation is
    built and the dial re-times neither.
    """
    names = default_names()
    captions = console_captions(club)
    assert names.display("tempo_2") not in captions
    assert not [c for c in captions if "gobo" in c.casefold() or "prism" in c.casefold()]


def test_2026_09_25_the_matrices_frame_names_no_bars_or_panels(club):
    """2026-09-25, Plan C final review: page 4 drew "patterns on the bars and panels".

    The club's matrices run on its pars and its heads: no fixture is made of
    pixels and none has built-in effects.
    """
    assert default_names().display("matrices_frame") not in console_captions(club)


def test_2026_09_25_the_library_help_names_no_built_in_effects(club):
    """2026-09-25, Plan C final review: page 4 spoke of "the panels' 42 built-in effects".

    Nothing on this rig has built-in effects, so no panels frame is built and
    the help lines about it have nothing to point at.
    """
    names = default_names()
    captions = console_captions(club)
    # library_2 and library_6 carry a {count} field, so are asserted by the panel/42 line.
    for key in ("library_1", "library_7"):
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


# 2026-09-26, round G: the rigs `newshow` refused since 2026-09-25 as below
# its minimum. (spec, count, channel width) of one model, in one row group.
SHAPES = {
    # Pars only: nothing pans or tilts, so no movement at all.
    "pars": ("Vortex|PC-64 LED S|Default|0|{address}|Par {index}", 6, 5),
    # Washes only: the MiN Wash has no dimmer channel, so no dimmer chase.
    "washes": ("Chauvet|MiN Wash|13 Channel|0|{address}|Wash {index}", 2, 13),
    # RGB heads: neither movement nor a dimmer, nor a strobe.
    "rgb": ("Stairville|CLB2.4 PAR head (split)|PAR|0|{address}|Head {index}", 4, 3),
}


@pytest.fixture(scope="module", params=sorted(SHAPES))
def shape(request, tmp_path_factory) -> tuple[str, Path]:
    folder = tmp_path_factory.mktemp(request.param)
    patch = build_single_shape_patch(folder, *SHAPES[request.param])
    out = folder / "show.qxw"
    assert main(["newshow", str(patch), "--out", str(out)]) == 0
    return request.param, out


def test_2026_09_26_a_pars_washes_or_rgb_only_rig_gets_a_show_check_passes(shape):
    """Pars only stopped at "no fixture in this workspace has both pan and
    tilt", washes only at "no fixture in this workspace has a dimmer"; since
    2026-09-25 both were refused up front. Now each builds and checks clean.
    """
    _, show = shape
    assert main(["check", str(show)]) == 0


def test_2026_09_26_the_console_promises_no_heads_or_dimmer_the_rig_lacks(shape):
    name, show = shape
    names = default_names()
    captions = console_captions(show)
    functions = {f.get("Name") for f in iter_local(Workspace.load(show).root, "Function")}
    moves = name == "washes"
    dims = name == "pars"
    assert (names.display("xy_pad") in captions) == moves
    assert (names.display("tempo_3") in captions) == moves
    assert (names.display("family_heads") in captions) == moves
    assert (names.display("dimmer_chase") in functions) == dims
    # No shape has a gobo or a prism; the tempo line names the dimmer or not.
    assert names.display(tempo_help_line(False, False, dims)) in captions
    assert (names.display("intensity_chases") in captions) == (name != "rgb")
    # Round G review: page 3's title names intensity only where its frame is.
    title = names.display(page_control_title(False, False, moves, name != "rgb"))
    assert title in captions
    assert ("intensi" in title.casefold()) == (name != "rgb")


def test_2026_09_26_the_caption_rule_bites_on_a_heads_promise(shape):
    """The page 3 title that names heads, put back on a rig without them."""
    name, show = shape
    if name == "washes":
        pytest.skip("the washes pan and tilt")
    names = default_names()
    root = Workspace.load(show).root
    title = names.display(page_control_title(False, False, False, name != "rgb"))
    widget = next(e for e in root.iter() if isinstance(e.tag, str) and e.get("Caption") == title)
    widget.set("Caption", names.display("page_control_no_haze_no_beam_wheel"))
    graph = build_show_graph(root, capabilities_of(root, FixtureLibrary.load()))
    findings = check_caption_promise(graph, root)
    assert [f.fields["identifier"] for f in findings] == ["page_control_no_haze_no_beam_wheel"]


@pytest.mark.skipif(qlcplus_binary() is None, reason="QLC+ is not installed on this machine")
def test_2026_09_26_qlcplus_loads_the_pars_washes_and_rgb_shows(shape):
    assert validate_workspace(shape[1]).errors == []


# Round G review, 2026-09-26: the rig minimum admitted rigs whose show failed
# its own check. One beam drew an empty two-colour-mix frame, two panels an
# empty matrices frame "on the panels". The page now draws neither empty frame
# and its help names neither; a rig newshow accepts must pass check.
REVIEW_SHAPES = {
    "beam": ("Generic|BEAM 230W 7R|16 channel|0|{address}|Beam {index}", 1, 16),
    "panels": ("HYULIGHTS|WX-60WPS-48PARTITION|A MODE - DMX 8 CH|0|{address}|Panel {index}", 2, 8),
    "bars": ("Stairville|CLB2.4 Compact LED PAR System|14 Channel|0|{address}|Bar {index}", 2, 14),
}


@pytest.mark.parametrize("name", sorted(REVIEW_SHAPES))
def test_2026_09_26_a_beam_panels_or_bars_only_rig_passes_its_own_check(name, tmp_path):
    patch = build_single_shape_patch(tmp_path, *REVIEW_SHAPES[name])
    show = tmp_path / "show.qxw"
    assert main(["newshow", str(patch), "--out", str(show)]) == 0
    assert main(["check", str(show)]) == 0
    names = default_names()
    captions = console_captions(show)
    has_mixes = names.display("mixes_frame") in captions
    has_matrices = any(
        names.display(matrices_frame_caption(bars, panels)) in captions
        for bars in (False, True)
        for panels in (False, True)
    )
    assert (has_mixes, has_matrices) == {
        "beam": (False, True),
        "panels": (True, False),
        "bars": (True, True),
    }[name]
    # Page 4's help is one of the two line sets chosen for what it draws.
    candidates = (
        library_help_lines(False, False, has_mixes, has_matrices),
        library_help_lines(True, name == "panels", has_mixes, has_matrices),
    )
    worded = [
        [names.display(k) for k in keys if k and "{count}" not in names.display(k)]
        for keys in candidates
    ]
    assert any(all(line in captions for line in lines) for lines in worded)
