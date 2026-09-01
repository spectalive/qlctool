"""Gobo, colour-wheel and prism scenes, read from the fixture definition."""

from pathlib import Path

import pytest

from qlctool import roles
from qlctool.generate.wheel_scenes import generate_wheel_scenes
from qlctool.library import FixtureLibrary
from qlctool.validate import qlcplus_binary, validate_workspace
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, localname

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"
BEAMS = (20, 21, 22, 23)  # the four BEAM 230W 7R, the only fixtures with gobos


def _functions(root):
    return {
        f.attrib["ID"]: f
        for f in find_local(root, "Engine")
        if localname(f) == "Function" and f.attrib.get("ID")
    }


def test_gobo_scenes_come_from_the_definition(tmp_path):
    ws = Workspace.load(SHOW)

    wheel = generate_wheel_scenes(ws, FixtureLibrary.load())

    # The BEAM definition names 20 gobo-wheel positions.
    assert len(wheel.scene_ids) == 20
    out = tmp_path / "out.qxw"
    ws.save(out)
    functions = _functions(Workspace.load(out).root)

    names = [functions[str(i)].attrib["Name"] for i in wheel.scene_ids]
    assert names[0] == "Gobo - White Light"
    assert "Gobo - Gobo 5" in names

    first = functions[str(wheel.scene_ids[1])]
    values = findall_local(first, "FixtureVal")
    # All four beams, each with the gobo channel set and its dimmer opened.
    assert sorted(int(v.attrib["ID"]) for v in values) == list(BEAMS)
    pairs = [int(x) for x in values[0].text.split(",")]
    assert dict(zip(pairs[0::2], pairs[1::2]))[9] == 10  # middle of 7-13


def test_prism_wheel_uses_the_prism_channel(tmp_path):
    ws = Workspace.load(SHOW)

    wheel = generate_wheel_scenes(
        ws,
        FixtureLibrary.load(),
        role=roles.PRISM,
        label="Prisma",
        run_order="Loop",
    )

    functions = _functions(ws.root)
    names = [functions[str(i)].attrib["Name"] for i in wheel.scene_ids]
    assert len(names) == 2  # prism off / prism on
    chaser = functions[str(wheel.chaser_id)]
    assert find_local(chaser, "RunOrder").text == "Loop"


def test_a_missing_wheel_is_an_error_not_an_empty_chaser():
    ws = Workspace.load(SHOW)
    with pytest.raises(ValueError, match="no fixture"):
        generate_wheel_scenes(ws, FixtureLibrary.load(), role="nonexistent-role", label="Nada")


@pytest.mark.skipif(qlcplus_binary() is None, reason="QLC+ is not installed on this machine")
def test_qlcplus_loads_wheel_scenes(tmp_path):
    ws = Workspace.load(SHOW)
    generate_wheel_scenes(ws, FixtureLibrary.load())
    out = tmp_path / "out.qxw"
    ws.save(out)

    assert validate_workspace(out).ok


def test_a_wheel_scene_drives_the_wheel_and_not_its_neighbour():
    """The BEAM 230W 7R has two Colour-group channels: the wheel at offset 7,
    with 17 named positions, and the continuous half-colour channel at offset 8.
    Both resolve to the colour-macro role. Sending the wheel's value to offset 8
    as well parks the wheel between two colours, which is what the show did
    before `wheel_for_role` existed."""
    from qlctool import roles
    from qlctool.capabilities_of import capabilities_of
    from qlctool.generate.wheel_scenes import generate_wheel_scenes
    from qlctool.library import FixtureLibrary
    from qlctool.workspace import Workspace
    from qlctool.xmlutil import find_local, findall_local, localname

    ws = Workspace.load(SHOW)
    library = FixtureLibrary.load()
    beams = [
        c.fixture.fixture_id for c in capabilities_of(ws.root, library) if c.has_role(roles.GOBO)
    ]
    assert beams

    beam = next(c for c in capabilities_of(ws.root, library) if c.fixture.fixture_id == beams[0])
    assert beam.offsets_for_role(roles.COLOR_MACRO) == [7, 8]
    assert beam.wheel_for_role(roles.COLOR_MACRO)[0] == 7

    result = generate_wheel_scenes(
        ws,
        library,
        role=roles.COLOR_MACRO,
        label="Color Beam",
        fixture_ids=beams,
        path="Color Beam",
    )
    scenes = {
        f.attrib["ID"]: f
        for f in find_local(ws.root, "Engine")
        if localname(f) == "Function" and f.attrib.get("ID")
    }
    for scene_id in result.scene_ids:
        for values in findall_local(scenes[str(scene_id)], "FixtureVal"):
            offsets = [int(v) for v in (values.text or "").split(",")[::2]]
            assert 8 not in offsets, f"scene {scene_id} still writes offset 8"
            assert 7 in offsets
