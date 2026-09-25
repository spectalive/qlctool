"""Spec step 3, completed 2026-09-25: Vibra described in English is a correct show.

The same patch, the same description, `language = "en"`: every name the
generator writes comes from the English catalogue, and every check that passes
on the Spanish show passes on this one.
"""

from dataclasses import replace

import pytest
from rig_root import RIG_ROOT

from qlctool.checks.run import check_workspace
from qlctool.desk_widgets import desk_widgets
from qlctool.deskmap import build_deskmap
from qlctool.generate.canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.names.load_catalogue import load_catalogue
from qlctool.validate import qlcplus_binary, validate_workspace
from qlctool.vibra.description import vibra_description
from qlctool.workspace import Workspace
from qlctool.xmlutil import iter_local

SETUPS = RIG_ROOT / "QLC+ Setups"
PLAY_PAGE = 1  # the console's second page, JUGAR / PLAY
LIBRARY_PAGE = 3


def _build(language: str, names: dict | None = None):
    workspace = Workspace.load(SETUPS / "Vibra.qxw")
    library = FixtureLibrary.load()
    description = replace(vibra_description(), language=language, names=names or {})
    show = build_canonical_show(
        workspace,
        library,
        plot_path=str(SETUPS / "vibra-stage-plot.json"),
        description=description,
    )
    return workspace, library, show


def _buttons_by_frame(workspace: Workspace, page: int) -> dict[str, list[str]]:
    """Each top-level frame of `page`, by caption in document order, with its buttons' captions."""
    widgets = desk_widgets(workspace.root)
    frames = {w.id: w for w in widgets if w.kind in ("Frame", "SoloFrame")}
    tops = {i for i, f in frames.items() if len(f.frames) == 2 and f.page == page}
    found: dict[str, list[str]] = {w.caption: [] for w in widgets if w.id in tops}
    for widget in widgets:
        top = next((f for f in widget.frames if f in tops), None)
        if widget.kind == "Button" and top is not None:
            found[frames[top].caption].append(widget.caption)
    return found


@pytest.fixture(scope="module")
def english():
    return _build("en")


@pytest.fixture(scope="module")
def spanish():
    return _build("es")


def test_the_console_speaks_english(english):
    workspace, _, show = english
    en = load_catalogue("en")
    # The room states are a solo frame (ruling P5): read both frame kinds.
    captions = {
        w.get("Caption", "")
        for tag in ("Frame", "SoloFrame")
        for w in iter_local(workspace.root, tag)
    }
    assert en["frames"]["room_states"] in captions
    assert en["frames"]["hits"] in captions
    assert "Party Moment" in show.master_ids
    assert "Momento Fiesta" not in show.master_ids


def test_every_check_passes(english):
    workspace, library, _ = english
    assert check_workspace(workspace, library) == []


def _desk_functions(workspace: Workspace) -> int:
    return sum(1 for f in iter_local(workspace.root, "Function") if f.get("Path") == "Desk")


@pytest.mark.parametrize(
    "hits",
    ["HITS — they punch through", "PUNCHES — they punch through"],
    ids=["explanation", "head"],
)
def test_a_frame_override_keeps_the_desk_bursts(english, hits):
    """2026-09-25, final review of Plan B (ruling F1): an override dropped the bursts.

    The desk bursts looked their frames up through the default vocabulary, so a
    renamed `hits` frame built 20 Desk functions instead of 34. Reading refuses
    a renamed head; the "head" case goes round reading to prove the generator
    itself follows the show's vocabulary.
    """
    workspace, _, _ = _build("en", {"en": {"hits": hits}})
    assert _desk_functions(workspace) == _desk_functions(english[0]) == 34


def test_the_desk_map_builds(english):
    workspace, library, _ = english
    deskmap = build_deskmap(workspace, library, "english.qxw")
    assert deskmap["controls"]


@pytest.mark.skipif(qlcplus_binary() is None, reason="QLC+ is not installed on this machine")
def test_qlcplus_loads_it(english, tmp_path):
    workspace, _, _ = english
    out = tmp_path / "Vibra-en.qxw"
    workspace.save(out)
    assert validate_workspace(out).errors == []


def test_the_play_page_keeps_every_button(english, spanish):
    """2026-09-25: Task 7 found English captions dropping JUGAR buttons.

    Frame by frame, in order, page two holds as many buttons in English as in
    Spanish: reset 11, colour hits 10, colour 25, pixels 15, heads 30, gobos 30,
    prism 11.
    """
    counts = {
        language: [len(b) for b in _buttons_by_frame(show[0], PLAY_PAGE).values()]
        for language, show in (("en", english), ("es", spanish))
    }
    assert counts["es"] == [11, 10, 25, 15, 30, 30, 11]
    assert counts["en"] == [11, 10, 25, 15, 30, 30, 11]


def test_the_library_page_writes_english_group_captions(english):
    """2026-09-25: the per-group wheels are rendered from the bank, cycles lose "Cycle "."""
    en = load_catalogue("en")
    wheels = _buttons_by_frame(english[0], LIBRARY_PAGE)[en["console"]["group_wheels_frame"]]
    assert en["console"]["group_colour_wheel_caption"].format(group="BarrasLed") in wheels
    assert en["console"]["group_mix_wheel_caption"].format(group="Lyres") in wheels
    assert "Panels" in wheels and "Matrices BarrasLed" in wheels
    assert not [caption for caption in wheels if caption.startswith("Cycle ")]


def test_the_play_page_picks_drop_their_markers(english):
    """2026-09-25: `_pick_caption` strips the English prefixes and suffixes (B8)."""
    captions = [c for b in _buttons_by_frame(english[0], PLAY_PAGE).values() for c in b]
    assert "↔ Circle" in captions and "▦ Effect 1" in captions and "✧ 1 and 3" in captions
    markers = ("Play · ", "Movement ", "Panels - ", "Prism - ", " + Pixels")
    assert not [c for c in captions if any(marker in c for marker in markers)]
