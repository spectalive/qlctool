"""Round G review, 2026-09-26: two patched fixtures sharing one ID are a finding.

The show graph keys capabilities by fixture ID, so a duplicated ID was one
entry and no rule said a word; QLC+ itself keeps one fixture per ID on load.
"""

from pathlib import Path

import pytest
from single_shape_rig import build_single_shape_patch

from qlctool.checks.check_workspace import check_workspace
from qlctool.checks.rule_duplicate_fixture_id import RULE_ID, check_duplicate_fixture_ids
from qlctool.cli import main
from qlctool.fixture_library import FixtureLibrary
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, iter_local

PARS = ("Vortex|PC-64 LED S|Default|0|{address}|Par {index}", 3, 5)


@pytest.fixture(scope="module")
def show(tmp_path_factory) -> Path:
    folder = tmp_path_factory.mktemp("pars")
    out = folder / "show.qxw"
    assert main(["newshow", str(build_single_shape_patch(folder, *PARS)), "--out", str(out)]) == 0
    return out


def _sharing_an_id(show: Path) -> Workspace:
    """The generated show with its second fixture repatched under the first one's ID."""
    workspace = Workspace.load(show)
    fixtures = [
        f for f in iter_local(workspace.root, "Fixture") if find_local(f, "Channels") is not None
    ]
    find_local(fixtures[1], "ID").text = find_local(fixtures[0], "ID").text
    return workspace


def test_2026_09_27_a_generated_show_shares_no_id(show):
    workspace = Workspace.load(show)
    assert check_duplicate_fixture_ids(workspace.root) == []
    assert [
        f for f in check_workspace(workspace, FixtureLibrary.load()) if f.rule_id == RULE_ID
    ] == []


def test_2026_09_27_two_fixtures_sharing_an_id_are_one_finding(show):
    workspace = _sharing_an_id(show)
    findings = check_duplicate_fixture_ids(workspace.root)
    assert [(f.function, f.fixtures, f.fields["count"]) for f in findings] == [
        ("ID 0", ("Par 1", "Par 2"), 2)
    ]


def test_2026_09_27_the_check_reports_the_shared_id_as_an_error(show):
    workspace = _sharing_an_id(show)
    findings = [
        f for f in check_workspace(workspace, FixtureLibrary.load()) if f.rule_id == RULE_ID
    ]
    assert [f.severity for f in findings] == ["error"]
    assert "ID 0" in str(findings[0]) and "Par 2" in str(findings[0])
