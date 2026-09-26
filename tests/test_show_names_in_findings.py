"""2026-09-26 (review of B10 round 2): a show's `[names]` overrides reach the finding text.

`named_findings` rendered with the shipped catalogue of the workspace's
language, so a show that renamed `full_white` still read the shipped name in
`wheel_white`'s message. A saved workspace records its language and not the
words its description renamed, so the description has to be handed in:
`check_workspace(..., names=...)` and `qlctool check --description`.
"""

import shutil
from pathlib import Path

from lxml import etree

from qlctool.checks.finding import ERROR, Finding
from qlctool.checks.named_findings import named_findings
from qlctool.checks.phrase import Phrase
from qlctool.cli import main
from qlctool.constants import QLC_NS
from qlctool.names.load_catalogue import load_catalogue
from qlctool.names.shipped_names import shipped_names
from qlctool.workspace import Workspace
from qlctool.xmlutil import iter_local

CLUB = Path(__file__).resolve().parents[1] / "examples" / "small-club"


def _wheel_white() -> Finding:
    return Finding(
        rule_id="wheel_white",
        severity=ERROR,
        function="Wheel Clock",
        message_id="wheel_white_on_clock",
        fields={"step": "Step 1", "count": 2, "full_white": Phrase("full_white"), "button": "B"},
    )


def test_a_renamed_function_is_named_by_its_new_name():
    root = Workspace.load(CLUB / "club.qxw").root
    names = shipped_names("en", {"en": {"full_white": "Work Light"}})
    shipped = named_findings([_wheel_white()], root)[0].message
    renamed = named_findings([_wheel_white()], root, names)[0].message
    assert load_catalogue("en")["functions"]["full_white"] in shipped
    assert "Work Light" in renamed
    assert load_catalogue("en")["functions"]["full_white"] not in renamed


def test_check_with_the_description_speaks_its_words(tmp_path, capsys):
    """End to end on the club: a Collection step with no id, reported as the
    description's word for "(empty)" once `--description` is given."""
    club = tmp_path / "club"
    shutil.copytree(CLUB, club)
    workspace = Workspace.load(club / "club.qxw")
    collection = next(
        f for f in iter_local(workspace.root, "Function") if f.get("Type") == "Collection"
    )
    etree.SubElement(collection, f"{{{QLC_NS}}}Step", Number="99").text = ""
    workspace.save(club / "club.qxw")
    description = club / "show.toml"
    description.write_text(
        description.read_text(encoding="utf-8")
        + '\n[names.en]\ndangling_reference_empty = "(no id at all)"\n',
        encoding="utf-8",
    )
    fixtures = ["--fixtures", str(club / "fixtures")]
    main([*fixtures, "check", str(club / "club.qxw")])
    said = capsys.readouterr().out
    assert load_catalogue("en")["findings"]["dangling_reference_empty"] in said
    assert "(no id at all)" not in said
    main([*fixtures, "check", "--description", str(description), str(club / "club.qxw")])
    assert "(no id at all)" in capsys.readouterr().out
