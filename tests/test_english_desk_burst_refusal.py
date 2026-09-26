"""2026-09-25: an English show with a broken desk burst is refused in English.

`build_deskmap` joined each finding's `message`, which outside `check_workspace`
is the Spanish rendering, so the refusal of an English show read in Spanish.
Since 2026-09-26 the frame around the findings follows the language as well.
"""

from copy import deepcopy
from dataclasses import replace

import pytest
from rig_root import RIG_ROOT

from qlctool.build_deskmap import build_deskmap
from qlctool.desk_burst_buttons import desk_burst_buttons
from qlctool.desk_burst_sources import desk_burst_sources
from qlctool.generate.build_canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.names.load_catalogue import load_catalogue
from qlctool.names.shipped_names import shipped_names
from qlctool.vibra.vibra_description import vibra_description
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, iter_local


def _with_two_step_burst(language: str) -> Workspace:
    workspace = Workspace.load(RIG_ROOT / "QLC+ Setups" / "Vibra.qxw")
    description = replace(vibra_description(), language=language)
    build_canonical_show(workspace, FixtureLibrary.load(), description=description)
    target = next(iter(desk_burst_buttons(workspace.root, shipped_names(language)).values()))[0]
    chaser = next(
        f for f in iter_local(workspace.root, "Function") if f.get("ID") == str(target.function)
    )
    chaser.append(deepcopy(find_local(chaser, "Step")))
    return workspace


@pytest.mark.parametrize("language", ["en", "es"])
def test_2026_09_25_the_burst_refusal_reads_in_the_show_language(language):
    workspace = _with_two_step_burst(language)
    with pytest.raises(ValueError) as refusal:
        build_deskmap(workspace, FixtureLibrary.load(), "unsaved.qxw")
    said = str(refusal.value)
    other = "es" if language == "en" else "en"
    assert load_catalogue(language)["findings"]["desk_burst_one_step"] in said
    assert load_catalogue(other)["findings"]["desk_burst_one_step"] not in said


@pytest.mark.parametrize("language", ["en", "es"])
def test_2026_09_26_the_refusal_frame_reads_in_the_show_language_too(language):
    """Review of round C: the findings were in the show's language, the frame
    around them ("invalid desk bursts: ") was English on a Spanish show."""
    workspace = _with_two_step_burst(language)
    with pytest.raises(ValueError) as refusal:
        build_deskmap(workspace, FixtureLibrary.load(), "unsaved.qxw")
    said = str(refusal.value)
    other = "es" if language == "en" else "en"
    frame = load_catalogue(language)["messages"]["desk_bursts_invalid"].split("{")[0]
    assert said.startswith(frame)
    assert load_catalogue(other)["messages"]["desk_bursts_invalid"].split("{")[0] not in said


@pytest.mark.parametrize("language", ["en", "es"])
def test_2026_09_26_an_accent_that_names_no_hit_is_refused_in_the_show_language(language):
    """Review of round D1: `desk_burst_no_accent` looked unreachable, and is not.
    A Toggle hand-copied into the colour hits, captioned so that its key is a
    burst's ("Red!!" beside RED) but its words spell no accent, reaches it."""
    names = shipped_names(language)
    workspace = Workspace.load(RIG_ROOT / "QLC+ Setups" / "Vibra.qxw")
    description = replace(vibra_description(), language=language)
    build_canonical_show(workspace, FixtureLibrary.load(), description=description)
    red = names.display("red")
    source = desk_burst_sources(workspace.root, names)[red.lower()]
    held = next(b for b in iter_local(workspace.root, "Button") if b.get("ID") == str(source.id))
    toggle = deepcopy(held)
    toggle.set("ID", "99999")
    toggle.set("Caption", f"{red}!!")
    find_local(toggle, "Action").text = "Toggle"
    held.addprevious(toggle)
    with pytest.raises(ValueError) as refusal:
        build_deskmap(workspace, FixtureLibrary.load(), "unsaved.qxw")
    said = str(refusal.value)
    frame = load_catalogue(language)["messages"]["desk_bursts_invalid"].split("{")[0]
    reason = load_catalogue(language)["messages"]["desk_burst_no_accent"].split("}")[1]
    assert said.startswith(frame)
    assert said.endswith(reason)
