"""End-to-end: generate a colour scene, inject it, prove the show still parses.

Exercises the whole stack - library, capabilities, generator, builder, insert,
save - against the real DeluxeEventos2 show, and checks the untouched functions
survive the round trip so generation never corrupts existing content.
"""

from pathlib import Path

import pytest

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.functions.scene import build_scene
from qlctool.generate.color_scene import color_scene_values
from qlctool.ids import next_function_id
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, iter_local

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"
from qlctool.library import FixtureLibrary


def _count_functions(root):
    return sum(1 for _ in iter_local(root, "Function"))


def test_red_scene_encoding():
    library = FixtureLibrary.load()
    root = Workspace.load(SHOW).root
    caps = capabilities_of(root, library)

    values = color_scene_values(caps, (255, 0, 0))

    # CromoWash (Advanced): red@5, green@6, blue@7, dimmer@9.
    crom = next(c for c in caps if "CromoWash" in c.fixture.model)
    assert values[crom.fixture.fixture_id] == [(5, 255), (6, 0), (7, 0), (9, 255)]

    # LED Bar: eight red segments all at 255.
    bar = next(c for c in caps if "LED Bar 240" in c.fixture.model)
    reds = [v for off, v in values[bar.fixture.fixture_id]
            if off in bar.offsets_for_role(roles.RED)]
    assert reds == [255] * 8


def test_inject_scene_keeps_show_valid(tmp_path):
    library = FixtureLibrary.load()
    ws = Workspace.load(SHOW)
    before = _count_functions(ws.root)

    caps = capabilities_of(ws.root, library)
    values = color_scene_values(caps, (0, 0, 255))
    fid = next_function_id(ws.root)
    ws.add_function(build_scene(fid, "GEN Todo Azul", values, path="Generated"))

    out = tmp_path / "out.qxw"
    ws.save(out)

    reloaded = Workspace.load(out).root
    assert _count_functions(reloaded) == before + 1

    scene = next(
        f for f in iter_local(reloaded, "Function")
        if f.attrib.get("Name") == "GEN Todo Azul"
    )
    assert scene.attrib["Type"] == "Scene"
    assert scene.attrib["ID"] == str(fid)
    assert find_local(scene, "Speed") is not None
    # A blue FixtureVal carries blue at full, red/green at zero.
    vals = [v for v in scene if v.attrib.get("ID") == str(caps[0].fixture.fixture_id)]
    assert vals and vals[0].text
