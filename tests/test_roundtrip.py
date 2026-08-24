"""The master safety net: loading and saving a real show must not change it.

Every generator the toolkit grows relies on this - if load -> save is lossless,
a surgical edit can only change the nodes it touched. These tests run against
the actual production workspaces in the repo, not fixtures.
"""

from pathlib import Path

import pytest
from lxml import etree

from qlctool.constants import DOCTYPE, XML_DECLARATION
from qlctool.workspace import Workspace
from qlctool.xmlsemantics import first_difference

REPO = Path(__file__).resolve().parents[3]
SETUPS = REPO / "QLC+ Setups"
WORKSPACES = sorted(SETUPS.glob("*.qxw"))


def test_workspaces_present():
    # If this fails the glob is wrong and every parametrized test is a false pass.
    assert WORKSPACES, f"no .qxw found under {SETUPS}"


@pytest.mark.parametrize("qxw", WORKSPACES, ids=lambda p: p.name)
def test_semantic_roundtrip(qxw: Path, tmp_path: Path):
    original_root = etree.parse(str(qxw)).getroot()

    ws = Workspace.load(qxw)
    out = tmp_path / qxw.name
    ws.save(out)

    reloaded_root = etree.parse(str(out)).getroot()
    diff = first_difference(original_root, reloaded_root)
    assert diff is None, f"{qxw.name} changed on round trip: {diff}"


@pytest.mark.parametrize("qxw", WORKSPACES, ids=lambda p: p.name)
def test_header_preserved(qxw: Path, tmp_path: Path):
    ws = Workspace.load(qxw)
    out = tmp_path / qxw.name
    ws.save(out)

    text = out.read_text(encoding="utf-8")
    assert text.startswith(f"{XML_DECLARATION}\n{DOCTYPE}\n")
    assert 'xmlns="http://www.qlcplus.org/Workspace"' in text
