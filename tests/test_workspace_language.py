"""Ruling B12 (2026-09-25): the desk reads a workspace in the language it was written in."""

from dataclasses import replace
from pathlib import Path

import pytest
from lxml import etree

from qlctool.deskmap import build_deskmap
from qlctool.generate.canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.names.load_catalogue import load_catalogue
from qlctool.names.workspace_language import workspace_language
from qlctool.vibra.description import vibra_description
from qlctool.workspace import Workspace

SHOW = Path(__file__).resolve().parents[3] / "QLC+ Setups" / "Vibra.qxw"


def _console(caption: str, kind: str = "Frame") -> etree._Element:
    return etree.fromstring(
        f'<Workspace><VirtualConsole><{kind} Caption="{caption}"/></VirtualConsole></Workspace>'
    )


@pytest.fixture(scope="module")
def english_show():
    """Vibra generated in English (ruling P12), a console the generator wrote."""
    workspace = Workspace.load(SHOW)
    build_canonical_show(
        workspace,
        FixtureLibrary.load(),
        description=replace(vibra_description(), language="en"),
    )
    return workspace


def test_the_shipped_show_is_spanish():
    assert workspace_language(Workspace.load(SHOW).root) == "es"


def test_an_english_room_frame_means_english():
    title = load_catalogue("en")["frames"]["room_states"]
    assert workspace_language(_console(title, "SoloFrame")) == "en"
    assert workspace_language(_console(title)) == "en"


def test_only_the_head_of_the_room_frame_counts():
    """2026-09-25: a reworded explanation or a changed case keeps the language."""
    head = load_catalogue("en")["frames"]["room_states"].split(" — ")[0]
    assert workspace_language(_console(f"{head.lower()} — pick one", "SoloFrame")) == "en"
    assert workspace_language(_console(head)) == "en"


def test_a_hand_built_console_is_read_as_spanish():
    assert workspace_language(_console("Anything")) == "es"


def test_a_generated_english_console_is_english(english_show):
    assert workspace_language(english_show.root) == "en"


def test_the_english_desk_map_speaks_english(english_show, tmp_path):
    english = load_catalogue("en")
    deskmap = build_deskmap(english_show, FixtureLibrary.load(), tmp_path / "show.qxw")
    titles = [page["title"] for page in deskmap["pages"]]
    assert titles[1] == english["frames"]["family_colour"]
    assert load_catalogue("es")["frames"]["family_colour"] not in titles
    sections = {s["key"]: s["title"] for page in deskmap["pages"] for s in page["sections"]}
    assert sections["state"] == english["console"]["desk_section_state"]
    controls = deskmap["controls"].values()
    assert english["help"]["desk_detail_not_stop"] in {c["detail"] for c in controls}
    burst_names = [
        f.get("Name") for f in english_show.engine if (f.get("Name") or "").startswith("Desk · ")
    ]
    assert burst_names and all("ráfaga" not in name for name in burst_names)
