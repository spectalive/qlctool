"""2026-09-25: an English show with a broken desk burst is refused in English.

`build_deskmap` joined each finding's `message`, which outside `check_workspace`
is the Spanish rendering, so the refusal of an English show read in Spanish.
"""

from copy import deepcopy
from dataclasses import replace

import pytest
from rig_root import RIG_ROOT

from qlctool.build_deskmap import build_deskmap
from qlctool.desk_burst_buttons import desk_burst_buttons
from qlctool.generate.canonical_show import build_canonical_show
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
    assert said.startswith("invalid desk bursts: ")
    other = "es" if language == "en" else "en"
    assert load_catalogue(language)["findings"]["desk_burst_one_step"] in said
    assert load_catalogue(other)["findings"]["desk_burst_one_step"] not in said
