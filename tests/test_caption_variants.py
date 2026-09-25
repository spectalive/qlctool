"""Page 1's tempo help and page 4's captions name only what the rig has (2026-09-25).

Plan C final review: the small club's console spoke of gobos, prism, bars,
panels and their 42 built-in effects, none of which it has.
"""

from pathlib import Path

import pytest
from console_captions import console_captions
from rig_root import RIG_ROOT
from small_rig import build_small_rig_patch

from qlctool.capabilities_of import capabilities_of
from qlctool.checks.check_workspace import check_workspace
from qlctool.cli import main
from qlctool.generate.library_help_lines import library_help_lines
from qlctool.generate.matrices_frame_caption import matrices_frame_caption
from qlctool.generate.panels_frame_caption import panels_frame_caption
from qlctool.generate.tempo_help_line import tempo_help_line
from qlctool.is_bar import is_bar
from qlctool.is_panel import is_panel
from qlctool.library import FixtureLibrary
from qlctool.names.default_names import default_names
from qlctool.names.shipped_names import shipped_names
from qlctool.workspace import Workspace

SETUPS = RIG_ROOT / "QLC+ Setups"
CLUB = Path(__file__).resolve().parents[1] / "examples" / "small-club"


@pytest.mark.parametrize(
    ("has_gobo", "has_prism", "key"),
    [
        (True, True, "tempo_2"),
        (True, False, "tempo_2_no_prism"),
        (False, True, "tempo_2_no_gobo"),
        (False, False, "tempo_2_no_gobo_no_prism"),
    ],
)
def test_2026_09_25_the_tempo_help_names_only_the_animations_the_show_built(
    has_gobo, has_prism, key
):
    assert tempo_help_line(has_gobo, has_prism) == key
    for language in ("en", "es"):
        line = shipped_names(language).display(key)
        assert ("gobo" in line) == has_gobo
        assert ("prism" in line) == has_prism


@pytest.mark.parametrize(
    ("has_bars", "has_panels", "key"),
    [
        (True, True, "matrices_frame"),
        (True, False, "matrices_frame_bars"),
        (False, True, "matrices_frame_panels"),
        (False, False, "matrices_frame_groups"),
    ],
)
def test_2026_09_25_the_matrices_frame_names_bars_and_panels_only_on_a_rig_with_them(
    has_bars, has_panels, key
):
    """2026-09-25, the owner's delegated decision: each noun only where the rig has it."""
    assert matrices_frame_caption(has_bars, has_panels) == key
    for language in ("en", "es"):
        caption = shipped_names(language).display(key)
        assert ("bar" in caption) == has_bars
        assert ("panel" in caption) == has_panels


@pytest.mark.parametrize("has_panels", [True, False])
def test_2026_09_25_the_built_in_effects_frame_says_panels_only_where_they_are(has_panels):
    for language in ("en", "es"):
        caption = shipped_names(language).render(panels_frame_caption(has_panels), count=17)
        assert "17" in caption
        assert ("anel" in caption) == has_panels


@pytest.mark.parametrize(
    ("has_builtin_effects", "has_panels"), [(True, True), (True, False), (False, False)]
)
def test_2026_09_25_the_library_help_speaks_of_built_in_effects_only_where_they_exist(
    has_builtin_effects, has_panels
):
    """The count is the rig's, filled in: 17 here, never a written-in 42; "panels" only on panels."""
    for language in ("en", "es"):
        names = shipped_names(language)
        lines = library_help_lines(has_builtin_effects, has_panels)
        text = " ".join(names.render(k, count=17) for k in lines if k)
        assert ("17" in text) == has_builtin_effects
        assert "42" not in text
        assert ("panel" in text) == has_panels


def test_2026_09_25_every_selectable_caption_has_a_promise_entry():
    """2026-09-25, review of `rotulo que promete lo que no hay`: five of the
    library lines were missing from `CAPTION_PROMISES`, and nothing tied the
    table to the selectors, so a new variant would go unjudged in silence.
    """
    from itertools import product

    from qlctool.checks.caption_promises import CAPTION_PROMISES
    from qlctool.generate.page_control_title import page_control_title

    chosen: set[str] = set()
    for first, second in product((False, True), repeat=2):
        chosen.add(tempo_help_line(first, second))
        chosen.add(matrices_frame_caption(first, second))
        chosen.add(page_control_title(first, second))
        chosen.add(panels_frame_caption(first))
        chosen.update(line for line in library_help_lines(first, second) if line is not None)
    assert chosen - set(CAPTION_PROMISES) == set()


def _rig_nouns(caps) -> tuple[bool, bool]:
    return any(is_bar(c) for c in caps), any(is_panel(c) for c in caps)


@pytest.fixture(scope="module")
def vibra_caps():
    return capabilities_of(Workspace.load(SETUPS / "Vibra.qxw").root, FixtureLibrary.load())


@pytest.mark.parametrize(
    ("keep", "key"),
    [
        ("all", "matrices_frame"),
        ("bars", "matrices_frame_bars"),
        ("panels", "matrices_frame_panels"),
        ("neither", "matrices_frame_groups"),
    ],
)
def test_2026_09_25_the_nouns_come_from_the_definitions(vibra_caps, keep, key):
    """Vibra's rig cut down to bars and no panels, panels and no bars, neither, both.

    The pars and every head stay in each cut, the MAC Wash's three rings
    included: a fixture with several heads that are not laid out in a line is
    not a bar, and a moving head is not a panel.
    """
    bars = [c for c in vibra_caps if is_bar(c)]
    panels = [c for c in vibra_caps if is_panel(c)]
    assert [c.fixture.fixture_id for c in bars] == [2, 3, 4, 5]
    assert [c.fixture.fixture_id for c in panels] == [24, 25, 27, 28]
    rest = [c for c in vibra_caps if c not in bars and c not in panels]
    cut = {"all": vibra_caps, "bars": rest + bars, "panels": rest + panels, "neither": rest}
    assert matrices_frame_caption(*_rig_nouns(cut[keep])) == key


def test_2026_09_25_a_rig_with_bars_and_no_panels_is_told_about_its_bars(tmp_path):
    """End to end: the club with two four-head CLB2.4 bars added; the checker agrees."""
    club = build_small_rig_patch(tmp_path)
    bars = ["--add", "Stairville|CLB2.4 Compact LED PAR System|14 Channel|0|200|Bar 1"]
    bars += ["--add", "Stairville|CLB2.4 Compact LED PAR System|14 Channel|0|220|Bar 2"]
    patch = tmp_path / "bars-patch.qxw"
    assert main(["patch", str(club), *bars, "--out", str(patch)]) == 0
    out = tmp_path / "bars.qxw"
    assert main(["newshow", str(patch), "--out", str(out)]) == 0
    names = default_names()
    captions = console_captions(out)
    assert names.display("matrices_frame_bars") in captions
    assert not [c for c in captions if "panel" in c.casefold()]
    assert check_workspace(Workspace.load(out), FixtureLibrary.load()) == []


def test_2026_09_25_the_club_has_neither_and_keeps_its_words():
    library = FixtureLibrary.load([CLUB / "fixtures"])
    caps = capabilities_of(Workspace.load(CLUB / "club-patch.qxw").root, library)
    assert caps
    assert _rig_nouns(caps) == (False, False)
    captions = console_captions(CLUB / "club.qxw")
    assert shipped_names("en").display("matrices_frame_groups") in captions
