"""The two intensity generators: a dimmer chase and the strobes.

Both are easy to get subtly wrong in ways QLC+ will not complain about - an EFX
in the wrong mode drives pan instead of intensity, and a strobe value picked off
an unlabelled shutter channel closes the head instead of flashing it.
"""

from pathlib import Path

import pytest

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.generate.dimmer_chases import MODE_DIMMER, generate_dimmer_chases
from qlctool.generate.strobe_effects import generate_strobe_effects
from qlctool.library import FixtureLibrary
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, localname

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


def _functions(root):
    return {
        int(f.attrib["ID"]): f
        for f in find_local(root, "Engine")
        if localname(f) == "Function" and f.attrib.get("ID")
    }


def test_the_dimmer_chase_is_an_efx_in_dimmer_mode(library):
    ws = Workspace.load(SHOW)
    generated = generate_dimmer_chases(ws, library)
    efx = _functions(ws.root)[generated.chase_id]

    assert efx.attrib["Type"] == "EFX"
    fixtures = findall_local(efx, "Fixture")
    assert fixtures
    for fixture in fixtures:
        assert find_local(fixture, "Mode").text == str(MODE_DIMMER)
    # Spread, not stacked: every fixture peaking together is just a dimmer.
    offsets = {find_local(f, "StartOffset").text for f in fixtures}
    assert len(offsets) == len(fixtures)


def test_the_dimmer_chase_leaves_the_smoke_machines_alone(library):
    ws = Workspace.load(SHOW)
    generated = generate_dimmer_chases(ws, library)
    functions = _functions(ws.root)

    smoke = {
        c.fixture.fixture_id
        for c in capabilities_of(ws.root, library)
        if c.is_smoke
    }
    driven = {
        int(find_local(f, "ID").text)
        for f in findall_local(functions[generated.chase_id], "Fixture")
    }
    assert not (driven & smoke)
    for scene_id in generated.scene_ids:
        touched = {
            int(v.attrib["ID"])
            for v in findall_local(functions[scene_id], "FixtureVal")
        }
        assert not (touched & smoke)


def test_the_ping_pong_scenes_are_complements(library):
    ws = Workspace.load(SHOW)
    generated = generate_dimmer_chases(ws, library)
    functions = _functions(ws.root)

    def lit(scene_id):
        values = {}
        for element in findall_local(functions[scene_id], "FixtureVal"):
            numbers = [int(n) for n in (element.text or "").split(",") if n != ""]
            values[int(element.attrib["ID"])] = numbers[1::2]
        return values

    first, second = (lit(i) for i in generated.scene_ids)
    assert first.keys() == second.keys()
    for fixture_id, levels in first.items():
        for a, b in zip(levels, second[fixture_id]):
            assert {a, b} == {0, 255}


def test_a_strobe_value_only_comes_from_a_labelled_range(library):
    """Never a guess: the value has to sit inside a range the definition calls
    a strobe, or the fixture is left out entirely."""
    ws = Workspace.load(SHOW)
    generated = generate_strobe_effects(ws, library, full_id=0, black_id=1)
    functions = _functions(ws.root)
    assert generated.on_id is not None

    ranges = {}
    for capability in capabilities_of(ws.root, library):
        for offset, caps in capability.capabilities_for_role(roles.STROBE):
            ranges[(capability.fixture.fixture_id, offset)] = caps

    driven = 0
    for element in findall_local(functions[generated.on_id], "FixtureVal"):
        fixture_id = int(element.attrib["ID"])
        numbers = [int(n) for n in (element.text or "").split(",") if n != ""]
        for offset, value in zip(numbers[0::2], numbers[1::2]):
            labels = ranges[(fixture_id, offset)]
            hit = [c for c in labels if c.minimum <= value <= c.maximum]
            assert hit, (fixture_id, offset, value)
            assert "strobe" in hit[0].name.lower(), hit[0].name
            driven += 1
    assert driven >= 3  # the CromoWash, the MiN Wash and the beams


def test_the_flash_strobes_step_the_looks_they_were_given(library):
    ws = Workspace.load(SHOW)
    generated = generate_strobe_effects(ws, library, full_id=42, black_id=43)
    functions = _functions(ws.root)

    for chaser_id, expected_hold in (
        (generated.fast_id, 50),
        (generated.medium_id, 250),
    ):
        chaser = functions[chaser_id]
        steps = findall_local(chaser, "Step")
        assert [s.text for s in steps] == ["42", "43"]
        assert all(int(s.attrib["Hold"]) == expected_hold for s in steps)
        assert find_local(chaser, "SpeedModes").attrib["Duration"] == "Common"
