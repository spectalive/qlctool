"""decompose -> compose must round-trip every real show losslessly.

This is the safety net for approach B (the git-diffable fragment tree): if
splitting and rebuilding changes nothing, editing a single function fragment is
safe. Runs against the actual production workspaces.
"""

from pathlib import Path

import pytest
from lxml import etree

from qlctool.compose import compose_workspace
from qlctool.decompose import FUNCTIONS_DIR, decompose_workspace
from qlctool.workspace import Workspace
from qlctool.xmlsemantics import first_difference
from qlctool.xmlutil import localname

REPO = Path(__file__).resolve().parents[3]
WORKSPACES = sorted((REPO / "QLC+ Setups").glob("*.qxw"))


def _engine_function_count(qxw: Path) -> int:
    # Only Engine's direct Function children are real functions; the same-named
    # references inside VC buttons and Collections are not decomposed.
    engine = Workspace.load(qxw).engine
    return sum(1 for c in engine if localname(c) == "Function")


@pytest.mark.parametrize("qxw", WORKSPACES, ids=lambda p: p.name)
def test_decompose_compose_roundtrip(qxw: Path, tmp_path: Path):
    original_root = etree.parse(str(qxw)).getroot()
    function_count = _engine_function_count(qxw)

    tree_dir = tmp_path / "tree"
    decompose_workspace(qxw, tree_dir)

    # One fragment file per function.
    fragments = list((tree_dir / FUNCTIONS_DIR).glob("*.xml"))
    assert len(fragments) == function_count

    rebuilt = tmp_path / "rebuilt.qxw"
    compose_workspace(tree_dir, rebuilt)

    rebuilt_root = etree.parse(str(rebuilt)).getroot()
    diff = first_difference(original_root, rebuilt_root)
    assert diff is None, f"{qxw.name} changed through decompose/compose: {diff}"
