"""The checks, and one test per bug that has actually happened in the room.

Split by topic out of the original `test_check.py` (over the codeality
test-file line cap): this file covers the small-club rig built by `newshow`
(Plan C preflight/final review, 2026-09-25) - dangling function references,
an empty console frame, a false-positive family owner, missing fixture
definitions, and caption promises the club's own patch cannot keep.
"""

import copy

import pytest
from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions
from lxml import etree
from named_show import named_show as _show
from small_rig import build_small_rig_patch

from qlctool.checks.check_workspace import check_workspace
from qlctool.checks.display_name_of_rule import display_name_of_rule
from qlctool.cli import main
from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.iter_local import iter_local
from qlctool.workspace import Workspace


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


@pytest.fixture(scope="module")
def _club_built(tmp_path_factory):
    """The small club's patch through `newshow`, built once."""
    folder = tmp_path_factory.mktemp("club")
    club = folder / "club.qxw"
    assert main(["newshow", str(build_small_rig_patch(folder)), "--out", str(club)]) == 0
    return Workspace.load(club).root


@pytest.fixture
def club_show(_club_built):
    """A private copy of the club's build, so a test that edits it changes no other."""
    return Workspace(etree.ElementTree(copy.deepcopy(_club_built)))


def _recaption(workspace, old, new):
    """Every console widget captioned `old` now says `new`; how many there were."""
    widgets = [
        e for e in workspace.root.iter() if isinstance(e.tag, str) and e.get("Caption") == old
    ]
    for widget in widgets:
        widget.set("Caption", new)
    return len(widgets)


def test_2026_09_25_a_collection_step_that_names_no_function(library):
    """2026-09-25, Plan C preflight: the first show built for a rig with no gobo
    wheel wrote `Talk Light` as the talk scene plus the beams' white, and there
    was no beams' white - `<Step Number="1">None</Step>`. QLC+ loaded it and
    every rule passed it, because the graph only follows steps that are
    numbers. Reproduced by putting that step back into the talk light, and a
    console button pointed at an id nothing carries beside it.
    """
    from qlctool.checks.rule_dangling_reference import RULE_ID
    from qlctool.constants import QLC_NS
    from qlctool.names.default_names import default_names

    workspace = _show()
    talk = _functions(workspace)[default_names().display("talk_light")]
    step = etree.SubElement(talk, f"{{{QLC_NS}}}Step")
    step.set("Number", str(len(findall_local(talk, "Step"))))
    step.text = "None"
    console = find_local(workspace.root, "VirtualConsole")
    button = next(b for b in iter_local(console, "Button") if find_local(b, "Function") is not None)
    find_local(button, "Function").set("ID", "999999")
    # A slider's <Adjust Function> is a reference too (Task 2a review): the
    # slider's own <Function> is left valid so only the Adjust can report it.
    slider = next(iter_local(console, "Slider"))
    etree.SubElement(slider, f"{{{QLC_NS}}}Adjust", Attribute="0", Function="999998")

    findings = [f for f in check_workspace(workspace, library) if f.rule_id == RULE_ID]
    assert {f.function for f in findings} == {
        default_names().display("talk_light"),
        button.get("Caption"),
        slider.get("Caption"),
    }
    assert any("None" in f.message for f in findings)
    assert any("999998" in f.message for f in findings)


def test_2026_09_25_a_frame_with_nothing_to_press(library, club_show):
    """2026-09-25, Plan C preflight (D9): the first show built for a rig with no
    haze machine put `HUMO AMBIENTE — cada cuánto dispara solo` on page 1 as a
    solo frame with no button in it, and `check` said "ningun problema".
    Reproduced on the small club (no haze machine): its console gets that
    empty haze frame back, and one frame holding only a label beside it.
    """
    from qlctool.checks.rule_empty_frame import RULE_ID
    from qlctool.constants import QLC_NS
    from qlctool.names.default_names import default_names
    from qlctool.vc.build_frame import build_frame
    from qlctool.vc.build_label import build_label
    from qlctool.vc.next_widget_id import next_widget_id

    workspace = club_show
    root = workspace.root
    outer = find_local(find_local(find_local(root, "VirtualConsole"), "Frame"), "Frame")
    haze = default_names().display("haze")
    build_frame(outer, next_widget_id(root), haze, 8, 770, 1000, 110, solo=True)
    words = build_frame(outer, next_widget_id(root), "Words only", 8, 900, 400, 60)
    build_label(words, next_widget_id(root), "a label over nothing", 6, 26, 300, 20)
    # An RGB matrix widget is a control: QLC+ writes it as <Matrix>.
    matrix = build_frame(outer, next_widget_id(root), "Matrix only", 420, 900, 400, 60)
    etree.SubElement(matrix, f"{{{QLC_NS}}}Matrix", ID=str(next_widget_id(root)))

    flagged = {f.function for f in check_workspace(workspace, library) if f.rule_id == RULE_ID}
    assert {haze, "Words only"} <= flagged
    assert "Matrix only" not in flagged
    # The page frame around them holds controls, so it is not flagged.
    assert f"marco {outer.get('ID')}" not in flagged


def test_2026_09_25_a_single_family_energy_cycle_is_not_a_family_owner(library, club_show):
    """2026-09-25, the small club (Plan C): a false positive, not a show bug.

    The club's energy cycle steps through level Collections that only move the
    heads - its pars have no pan/tilt and its dimmer levels sit inside the
    steps - so it writes one family. `family_frame_problems` counted a Chaser as a
    structural cycle only when it wrote two or more families, took this one
    for the position family's owner, and reported "familia con dueño: <energy
    cycle>: no tiene su Toggle en el marco" and "capa pisada por el ciclo:
    <heads centre>". Vibra's own cycle writes several families, which is why
    no shipped workspace showed it.
    """
    findings = check_workspace(club_show, library)
    assert [f for f in findings if f.rule_id in ("family_owner", "pick_overridden")] == []


def test_2026_09_25_a_patched_fixture_with_no_definition(tmp_path, monkeypatch, capsys):
    """2026-09-25, Plan C final review: `qlctool check examples/small-club/club.qxw`
    from the toolkit root warned "no fixture definition ... searched no folder"
    and printed `199 botones revisados, ningun problema`: a false pass, since
    every rule reasons about channels a fixture with no definition does not
    have. The club is copied where no walk-up finds a folder; the missing
    definitions are findings now, and the run exits non-zero.
    """
    import shutil
    from pathlib import Path

    from qlctool.checks.rule_missing_definition import RULE_ID

    example = Path(__file__).resolve().parents[1] / "examples" / "small-club"
    club = tmp_path / "club.qxw"
    shutil.copy(example / "club.qxw", club)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("QLCTOOL_FIXTURES", raising=False)
    assert main(["check", str(club)]) == 1
    printed = capsys.readouterr().out
    # The club is an English show: since ruling B10 its rule names are English.
    assert f"  {display_name_of_rule(RULE_ID, 'en')} (3):" in printed
    assert "Chauvet MiN Wash" in printed
    # Since round 2 of ruling B10 its finding messages are English too.
    assert "searched: no folder" in printed
    assert "buscado" not in printed

    assert main(["--fixtures", str(example / "fixtures"), "check", str(club)]) == 0
    assert "199 buttons checked, no problems" in capsys.readouterr().out


def test_2026_09_25_a_known_model_patched_in_a_mode_its_definition_lacks(tmp_path, capsys):
    """2026-09-25, review of `sin definicion`: `capabilities_of` also drops a
    fixture whose definition exists but has no mode of the patched name, and
    every rule is as blind to it as to a missing definition - the same false
    pass. One MiN Wash of the club is repatched into a mode the definition
    does not carry; the check names the model, the mode and that fixture.
    """
    from pathlib import Path

    from qlctool.checks.rule_missing_definition import RULE_ID
    from qlctool.find_local import find_local
    from qlctool.iter_local import iter_local
    from qlctool.names.shipped_names import shipped_names

    example = Path(__file__).resolve().parents[1] / "examples" / "small-club"
    workspace = Workspace.load(example / "club.qxw")
    wash = next(
        f
        for f in iter_local(workspace.root, "Fixture")
        if find_local(f, "Name") is not None and find_local(f, "Name").text == "Wash 1"
    )
    find_local(wash, "Mode").text = "No Such Mode"
    club = tmp_path / "club.qxw"
    workspace.save(club)

    library = FixtureLibrary.load([example / "fixtures"])
    findings = [f for f in check_workspace(Workspace.load(club), library) if f.rule_id == RULE_ID]
    # The club is an English show, so the message is the English entry (B10, round 2).
    message = shipped_names("en").render("missing_mode", mode="No Such Mode")
    assert [(f.function, f.message, f.fixtures) for f in findings] == [
        ("Chauvet MiN Wash (No Such Mode)", message, ("Wash 1",))
    ]
    assert main(["--fixtures", str(example / "fixtures"), "check", str(club)]) == 1
    assert f"  {display_name_of_rule(RULE_ID, 'en')} (1):" in capsys.readouterr().out


def test_2026_09_25_a_caption_that_promises_gobos_and_prism(library, club_show):
    """2026-09-25, Plan C final review: page 1 said "gobos, prisma y dimmer siguen
    tu compas" on the small club, whose LED Beam heads have no gobo or prism
    wheel, and `check` said "ningun problema". The club's own tempo line is
    replaced with the catalogue's `tempo_2`; the untouched club has no finding.
    """
    from qlctool.checks.rule_caption_promise import RULE_ID
    from qlctool.names.shipped_names import shipped_names

    assert [f for f in check_workspace(club_show, library) if f.rule_id == RULE_ID] == []
    names = shipped_names("es")
    promise = names.display("tempo_2")
    assert _recaption(club_show, names.display("tempo_2_no_gobo_no_prism"), promise) == 1
    findings = [f for f in check_workspace(club_show, library) if f.rule_id == RULE_ID]
    assert [f.function for f in findings] == [promise]
    assert "rueda de gobos" in findings[0].message and "prisma" in findings[0].message


def test_2026_09_25_a_caption_that_promises_bars_panels_and_their_effects(library, club_show):
    """2026-09-25, Plan C final review: page 4's matrices frame said "patterns on
    the bars and panels" and its help "the panels' 42 built-in effects" on the
    small club, which has no pixel group and nothing with built-in effects.
    Both captions are put back, in English: the lookup reads every shipped
    catalogue, and a `{count}` field matches any number.
    """
    from qlctool.checks.rule_caption_promise import RULE_ID
    from qlctool.names.shipped_names import shipped_names

    spanish, english = shipped_names("es"), shipped_names("en")
    matrices = english.display("matrices_frame")
    effects = english.render("library_2", count=42)
    assert _recaption(club_show, spanish.display("matrices_frame_groups"), matrices) == 1
    assert _recaption(club_show, spanish.display("library_2_no_builtins"), effects) == 1
    findings = {
        f.function: f.message for f in check_workspace(club_show, library) if f.rule_id == RULE_ID
    }
    assert set(findings) == {matrices, effects}
    # Since the owner's delegated decision (2026-09-25) the nouns are the
    # promises: a bar (`is_bar`) and a panel (`is_panel`).
    assert "barra de pixeles" in findings[matrices]
    assert "panel con efectos propios" in findings[matrices]
    assert "panel con efectos propios" in findings[effects]
    assert "barra de pixeles" not in findings[effects]
