"""An English show's check reads in English (ruling B10, round 1, 2026-09-25).

Until this date every finding of an English show was still headed by a Spanish
rule name - "marco vacio (1):" over a console that said "Room States" - and a
clean English show was summed up as "N botones revisados, ningun problema".
The rule names and the summary lines now come from the workspace's catalogue.

Round 2, the same day: the messages still read "este marco no tiene ningun
control dentro" under "empty frame (1):", and the club's missing definitions
said "buscado en ninguna carpeta". Every message is now a `[findings]` entry
rendered in the workspace's language (`checks/named_findings.py`).
"""

import re
import shutil
from dataclasses import replace
from pathlib import Path

import pytest
from rig_root import RIG_ROOT

from qlctool.checks.check_workspace import check_workspace
from qlctool.checks.joined import Joined
from qlctool.checks.phrase import Phrase
from qlctool.checks.rendered_value import rendered_value
from qlctool.checks.rule_empty_frame import check_empty_frames
from qlctool.cli import main
from qlctool.generate.canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.names.load_catalogue import load_catalogue
from qlctool.names.shipped_names import shipped_names
from qlctool.print_check_report import print_check_report
from qlctool.vc.frame import build_frame
from qlctool.vc.label import build_label
from qlctool.vc.widget_ids import next_widget_id
from qlctool.vibra.vibra_description import vibra_description
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local

SETUPS = RIG_ROOT / "QLC+ Setups"
CLUB = Path(__file__).resolve().parents[1] / "examples" / "small-club" / "club.qxw"
WORD = r"[^\W\d_]{4,}"


def _spanish_only_words() -> set[str]:
    """Words of the Spanish `[findings]` entries that their English twins do not use."""
    spanish, english = load_catalogue("es")["findings"], load_catalogue("en")["findings"]
    words: set[str] = set()
    for identifier, text in spanish.items():
        same = set(re.findall(WORD, english[identifier]))
        words |= {w for w in re.findall(WORD, text) if w not in same}
    return words


def _spanish_in(text: str) -> list[str]:
    return sorted(set(re.findall(WORD, text)) & _spanish_only_words())


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


@pytest.fixture
def english(library):
    """Vibra described in English, as `tests/test_english_vibra.py` builds it."""
    workspace = Workspace.load(SETUPS / "Vibra.qxw")
    description = replace(vibra_description(), language="en")
    build_canonical_show(
        workspace,
        library,
        plot_path=str(SETUPS / "vibra-stage-plot.json"),
        description=description,
    )
    return workspace


def _with_an_empty_frame(workspace):
    """The empty frame of `test_check.py` (Plan C preflight, D9), put back in."""
    root = workspace.root
    outer = find_local(find_local(find_local(root, "VirtualConsole"), "Frame"), "Frame")
    words = build_frame(outer, next_widget_id(root), "Words only", 8, 900, 400, 60)
    build_label(words, next_widget_id(root), "a label over nothing", 6, 26, 300, 20)
    return root


def test_2026_09_25_an_english_shows_findings_are_named_in_english(english, library, capsys):
    """The empty frame put back into the English Vibra: the finding is
    `empty_frame`, headed "empty frame"."""
    root = _with_an_empty_frame(english)

    findings = check_workspace(english, library)
    empty = [f for f in findings if f.function == "Words only" and f.rule_id == "empty_frame"]
    assert [f.rule for f in empty] == [load_catalogue("en")["checks"]["empty_frame"]]
    spanish = set(load_catalogue("es")["checks"].values()) - set(
        load_catalogue("en")["checks"].values()
    )
    assert not {f.rule for f in findings} & spanish

    assert print_check_report("show.qxw", root, findings, limit=3) == 1
    printed = capsys.readouterr().out
    assert printed.startswith(f"show.qxw: {len(findings)} problem(s) in ")
    assert "\n  empty frame (1):\n" in printed
    assert "marco vacio" not in printed


def test_2026_09_25_a_clean_english_show_is_summed_up_in_english(english, library, capsys):
    assert check_workspace(english, library) == []
    assert print_check_report("show.qxw", english.root, [], limit=3) == 0
    printed = capsys.readouterr().out
    assert printed.endswith(" buttons checked, no problems\n")
    assert "botones" not in printed


def test_2026_09_25_an_english_shows_findings_say_what_they_found_in_english(
    english, library, capsys
):
    """Round 2: the same injected bug, and every message is the English entry."""
    root = _with_an_empty_frame(english)
    findings = check_workspace(english, library)
    empty = [f for f in findings if f.function == "Words only" and f.rule_id == "empty_frame"]
    english_entries = load_catalogue("en")["findings"]
    assert [f.message for f in empty] == [english_entries["empty_frame_nothing_to_press"]]
    assert {f.message_id for f in findings} >= {
        "empty_frame_nothing_to_press",
        "console_off_screen",
    }
    assert {f.message: _spanish_in(f.message) for f in findings if _spanish_in(f.message)} == {}

    print_check_report("show.qxw", root, findings, limit=3)
    printed = capsys.readouterr().out
    assert f"    Words only: {english_entries['empty_frame_nothing_to_press']}\n" in printed
    assert _spanish_in(printed) == []


def test_2026_09_25_the_clubs_missing_definitions_read_in_english_end_to_end(
    tmp_path, monkeypatch, capsys
):
    """`qlctool check club.qxw` with no fixture folder: the club is an English
    show, and its finding said "buscado en ninguna carpeta" until round 2."""
    club = tmp_path / "club.qxw"
    shutil.copy(CLUB, club)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("QLCTOOL_FIXTURES", raising=False)
    assert main(["check", str(club)]) == 1
    printed = capsys.readouterr().out
    names = shipped_names("en")
    said = names.render("missing_definition", searched=names.display("searched_no_folder"))
    assert f"    Chauvet MiN Wash: {said}  [Wash 1, Wash 2]\n" in printed
    assert _spanish_in(printed) == []


def test_2026_09_25_a_rule_called_on_its_own_still_reads_in_spanish(english):
    """Outside `check_workspace` nobody has asked the workspace's language."""
    findings = check_empty_frames(_with_an_empty_frame(english))
    spanish = load_catalogue("es")["findings"]["empty_frame_nothing_to_press"]
    assert [f.message for f in findings if f.function == "Words only"] == [spanish]


def test_2026_09_25_a_list_and_a_catalogue_word_are_said_in_the_language():
    clocks = Joined(("«A»", "«B»"), Phrase("list_and"))
    assert rendered_value(shipped_names("en"), clocks) == "«A» and «B»"
    assert rendered_value(shipped_names("es"), clocks) == "«A» y «B»"
    promise = Phrase(
        "caption_promise_missing", {"identifier": "tempo_2", "promises": Phrase("promise_prism")}
    )
    assert "promises a prism" in str(rendered_value(shipped_names("en"), promise))
