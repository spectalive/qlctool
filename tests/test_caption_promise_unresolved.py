"""Round G review, 2026-09-26: when the caption rule steps aside for an unread fixture.

The rule said nothing while more fixtures were patched than the graph held
capabilities for. That count also went short when two fixtures share an ID,
which the graph keeps as one entry, so a sound rig with a duplicated ID was
never judged. The rule now asks, fixture by fixture, whether its definition
was read.
"""

from pathlib import Path

import pytest
from single_shape_rig import build_single_shape_patch

from qlctool.capabilities_of import capabilities_of
from qlctool.checks.rule_caption_promise import check_caption_promise
from qlctool.checks.show_graph import build_show_graph
from qlctool.cli import main
from qlctool.library import FixtureLibrary
from qlctool.names.default_names import default_names
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, iter_local

PARS = ("Vortex|PC-64 LED S|Default|0|{address}|Par {index}", 3, 5)
PROMISE = "page_control_no_haze_no_beam_wheel"


@pytest.fixture(scope="module")
def show(tmp_path_factory) -> Path:
    """A pars-only show whose page 3 title is put back to one promising heads."""
    folder = tmp_path_factory.mktemp("pars")
    out = folder / "show.qxw"
    assert main(["newshow", str(build_single_shape_patch(folder, *PARS)), "--out", str(out)]) == 0
    return out


def _promising_heads(show: Path):
    names = default_names()
    root = Workspace.load(show).root
    title = names.display("page_control_no_haze_no_heads")
    widget = next(e for e in root.iter() if isinstance(e.tag, str) and e.get("Caption") == title)
    widget.set("Caption", names.display(PROMISE))
    return root


def _identifiers(root, caps) -> list[str]:
    return [
        f.fields["identifier"] for f in check_caption_promise(build_show_graph(root, caps), root)
    ]


def test_2026_09_26_the_rule_bites_when_every_definition_is_read(show):
    root = _promising_heads(show)
    assert _identifiers(root, capabilities_of(root, FixtureLibrary.load())) == [PROMISE]


def test_2026_09_26_one_missing_definition_makes_the_rule_step_aside(show):
    root = _promising_heads(show)
    caps = capabilities_of(root, FixtureLibrary.load())
    assert _identifiers(root, caps[1:]) == []


def test_2026_09_26_two_fixtures_sharing_an_id_do_not_silence_the_rule(show):
    root = _promising_heads(show)
    fixtures = [f for f in iter_local(root, "Fixture") if find_local(f, "Channels") is not None]
    first_id = find_local(fixtures[0], "ID").text
    find_local(fixtures[1], "ID").text = first_id
    assert _identifiers(root, capabilities_of(root, FixtureLibrary.load())) == [PROMISE]
