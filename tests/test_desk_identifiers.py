"""The desk places controls by frame identifier, not by Spanish words (2026-09-24).

Spec: "Checks and the desk map resolve widgets through the identifiers, never
through the Spanish strings they search for today." Renaming every console frame
to its English catalogue spelling must leave the desk's pages exactly as they were.
"""

from copy import deepcopy

import pytest
from rig_root import RIG_ROOT

from qlctool.build_deskmap import build_deskmap
from qlctool.desk_burst_duration import desk_burst_duration
from qlctool.desk_widgets import DeskWidget
from qlctool.generate.canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.names.default_names import default_names
from qlctool.names.load_catalogue import load_catalogue
from qlctool.workspace import Workspace

SHOW = RIG_ROOT / "QLC+ Setups" / "Vibra.qxw"


@pytest.fixture(scope="module")
def generated():
    workspace = Workspace.load(SHOW)
    build_canonical_show(workspace, FixtureLibrary.load())
    return workspace


def _frames_in_english(workspace):
    """Renamed workspace, plus how many captions actually changed.

    The count guards the test above it against going vacuous if the frames
    catalogue drifts and stops matching anything in the shipped show.
    """
    translated = deepcopy(workspace)
    spanish, english = load_catalogue("es")["frames"], load_catalogue("en")["frames"]
    replaced = 0
    for element in translated.root.iter():
        for identifier, text in spanish.items():
            if element.get("Caption") == text:
                element.set("Caption", english[identifier])
                replaced += 1
    return translated, replaced


def _sections(deskmap):
    return [(p["key"], s["key"], s["controls"]) for p in deskmap["pages"] for s in p["sections"]]


def test_the_desk_places_frames_named_in_any_shipped_language(generated, tmp_path):
    library = FixtureLibrary.load()
    translated, replaced = _frames_in_english(generated)
    assert replaced >= len(load_catalogue("es")["frames"])
    spanish = build_deskmap(generated, library, tmp_path / "show.qxw")
    english = build_deskmap(translated, library, tmp_path / "show.qxw")
    assert _sections(english) == _sections(spanish)


@pytest.mark.parametrize(
    ("caption", "duration"),
    [
        ("⚡ FLASH LENTO · -", 8000),
        ("ROJO", 8000),
        ("RED", 8000),
        ("☁ HUMO YA", 3000),
        ("✳ STROBE", 4000),
        ("Rig Rojo / Azul", None),
    ],
)
def test_a_burst_lasts_what_its_identifier_says(caption, duration):
    widget = DeskWidget(
        id=1,
        kind="Button",
        caption=caption,
        page=0,
        function=1,
        action="Flash",
        key=None,
        frames=(),
        solo=None,
        fade_out_ms=0,
        slider_mode="",
    )
    assert desk_burst_duration(widget, default_names()) == duration
