"""2026-09-25: a known model in a mode its definition lacks is told to repatch.

`warn_unresolved` said "no fixture definition ... pass --fixtures" for every
fixture `resolved_definition` rejected, also when the definition was found
and only the patched mode was missing from it - advice that cannot help,
since the folder is already right. The warning now names the model, the mode
and the modes the definition has, and asks for a repatch.
"""

from pathlib import Path

from rig_root import RIG_ROOT
from small_rig import build_small_rig_patch

from qlctool.cli import main
from qlctool.description.description_names import description_names
from qlctool.library import FixtureLibrary
from qlctool.vibra.vibra_description import vibra_description
from qlctool.warn_unresolved import warn_unresolved
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, iter_local

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "small-club"


def test_2026_09_25_newshow_tells_a_known_model_in_a_missing_mode_to_repatch(tmp_path, capsys):
    patch = build_small_rig_patch(tmp_path)
    workspace = Workspace.load(patch)
    wash = next(
        fixture
        for fixture in iter_local(workspace.root, "Fixture")
        if find_local(fixture, "Name") is not None and find_local(fixture, "Name").text == "Wash 1"
    )
    find_local(wash, "Mode").text = "No Such Mode"
    workspace.save(patch)
    capsys.readouterr()

    assert main(["newshow", str(patch), "--out", str(tmp_path / "club.qxw")]) == 0
    printed = capsys.readouterr().err
    # The vocabulary `newshow` warns in: the show's, which with no description
    # is the Vibra description's.
    expected = description_names(vibra_description()).render(
        "unresolved_mode", model="Chauvet MiN Wash", mode="No Such Mode", modes="13 Channel"
    )
    assert printed == f"qlctool: {expected}\n"
    assert "--fixtures" not in printed


def test_2026_09_25_the_shipped_shows_are_warned_about_nothing(capsys):
    shows = [
        (RIG_ROOT / "QLC+ Setups" / name, FixtureLibrary.load())
        for name in ("Vibra.qxw", "Vibra-beats.qxw", "Vibra-split.qxw")
    ]
    shows.append((EXAMPLE / "club.qxw", FixtureLibrary.load([EXAMPLE / "fixtures"])))
    for path, library in shows:
        warn_unresolved(Workspace.load(path).root, library)
        assert capsys.readouterr().err == "", path.name
