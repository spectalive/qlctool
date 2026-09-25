"""An English show's check reads in English (ruling B10, round 1, 2026-09-25).

Until this date every finding of an English show was still headed by a Spanish
rule name - "marco vacio (1):" over a console that said "Room States" - and a
clean English show was summed up as "N botones revisados, ningun problema".
The rule names and the summary lines now come from the workspace's catalogue;
the finding messages are round 2 and may still be Spanish.
"""

from dataclasses import replace

import pytest
from rig_root import RIG_ROOT

from qlctool.checks.run import check_workspace
from qlctool.generate.canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.names.load_catalogue import load_catalogue
from qlctool.print_check_report import print_check_report
from qlctool.vc.frame import build_frame
from qlctool.vc.label import build_label
from qlctool.vc.widget_ids import next_widget_id
from qlctool.vibra.vibra_description import vibra_description
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local

SETUPS = RIG_ROOT / "QLC+ Setups"


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


def test_2026_09_25_an_english_shows_findings_are_named_in_english(english, library, capsys):
    """The empty frame of `test_check.py` (Plan C preflight, D9) put back into
    the English Vibra: the finding is `empty_frame`, headed "empty frame"."""
    root = english.root
    outer = find_local(find_local(find_local(root, "VirtualConsole"), "Frame"), "Frame")
    words = build_frame(outer, next_widget_id(root), "Words only", 8, 900, 400, 60)
    build_label(words, next_widget_id(root), "a label over nothing", 6, 26, 300, 20)

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
