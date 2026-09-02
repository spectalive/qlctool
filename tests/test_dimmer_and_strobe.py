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
from qlctool.generate.dimmer_sequence import generate_dimmer_sequence
from qlctool.generate.energy_intensity import generate_energy_intensity
from qlctool.generate.strobe_effects import generate_strobe_effects
from qlctool.library import FixtureLibrary
from qlctool.shutter_open import shutter_open_pairs
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


def _chase_efx(root, chase_id):
    """The EFX under a dimmer chase: itself, or its Collection's members.

    2026-08-28: the chase went back to the hand-built shape - one Serial Line
    cascade per fixture family, gathered in a Collection - so a chase on a
    multi-family rig is a Collection and on a one-family rig a plain EFX.
    """
    functions = _functions(root)
    function = functions[chase_id]
    if function.attrib["Type"] == "EFX":
        return [function]
    assert function.attrib["Type"] == "Collection"
    return [functions[int(step.text)] for step in findall_local(function, "Step")]


def test_the_dimmer_chase_is_a_family_cascade_in_dimmer_mode(library):
    """2026-08-28: the hand-built show ran a Serial Line cascade per fixture
    family (Dimmer Chase CromoWash, ... PC LED, ... Beam 7R); the whole-rig
    Circle that replaced them lost the look. Each family EFX must be a Serial
    Line in Dimmer mode with the pan term killed.
    """
    ws = Workspace.load(SHOW)
    generated = generate_dimmer_chases(ws, library)
    parts = _chase_efx(ws.root, generated.chase_id)

    assert len(parts) > 1  # this rig has several dimmable families
    for efx in parts:
        assert efx.attrib["Type"] == "EFX"
        assert find_local(efx, "Algorithm").text == "Line"
        assert find_local(efx, "Width").text == "0"
        assert find_local(efx, "PropagationMode").text == "Serial"
        fixtures = findall_local(efx, "Fixture")
        assert fixtures
        for fixture in fixtures:
            assert find_local(fixture, "Mode").text == str(MODE_DIMMER)
        # Spread, not stacked: every fixture peaking together is a dimmer.
        offsets = {find_local(f, "StartOffset").text for f in fixtures}
        assert len(offsets) == len(fixtures)


def test_the_second_dimmer_chase_runs_backwards(library):
    """2026-08-27: DeluxeEventos2 had two sweeps on V and B, but the
    generated show kept only the forward one. The second sweep must reverse
    every fixture rather than merely rename the same effect.
    """
    ws = Workspace.load(SHOW)
    generated = generate_dimmer_chases(ws, library)

    forward = [
        f for efx in _chase_efx(ws.root, generated.chase_id) for f in findall_local(efx, "Fixture")
    ]
    backward = [
        f for efx in _chase_efx(ws.root, generated.chase2_id) for f in findall_local(efx, "Fixture")
    ]
    assert forward and backward
    assert all(find_local(f, "Direction").text == "Forward" for f in forward)
    assert all(find_local(f, "Direction").text == "Backward" for f in backward)


def test_the_dimmer_sequence_breathes_between_all_three_programs(library):
    """2026-08-27: the generated show lost DeluxeEventos2's steady breath
    between its three dimmer sweeps. Restore the exact six-step rotation so
    every moving programme returns to full light before the next one.
    """
    ws = Workspace.load(SHOW)
    dimmers = generate_dimmer_chases(ws, library)
    intensity = generate_energy_intensity(ws, capabilities_of(ws.root, library))
    assert intensity.full_id is not None
    programs = [dimmers.chase_id, dimmers.pingpong_id, dimmers.chase2_id]

    sequence_id = generate_dimmer_sequence(ws, breath_id=intensity.full_id, program_ids=programs)
    chaser = _functions(ws.root)[sequence_id]
    steps = findall_local(chaser, "Step")

    assert chaser.attrib["Name"] == "Dimmer Secuencia"
    assert find_local(chaser, "RunOrder").text == "Loop"
    assert find_local(chaser, "SpeedModes").attrib["Duration"] == "PerStep"
    assert [int(step.text) for step in steps] == [
        intensity.full_id,
        dimmers.chase_id,
        intensity.full_id,
        dimmers.pingpong_id,
        intensity.full_id,
        dimmers.chase2_id,
    ]
    assert [int(step.attrib["Hold"]) for step in steps] == [
        20000,
        10000,
        20000,
        10000,
        20000,
        10000,
    ]


def test_the_dimmer_chase_leaves_the_smoke_machines_alone(library):
    ws = Workspace.load(SHOW)
    generated = generate_dimmer_chases(ws, library)
    functions = _functions(ws.root)

    smoke = {c.fixture.fixture_id for c in capabilities_of(ws.root, library) if c.is_smoke}
    driven = {
        int(find_local(f, "ID").text)
        for f in findall_local(functions[generated.chase_id], "Fixture")
    }
    assert not (driven & smoke)
    for scene_id in generated.scene_ids:
        touched = {int(v.attrib["ID"]) for v in findall_local(functions[scene_id], "FixtureVal")}
        assert not (touched & smoke)


def test_the_ping_pong_scenes_are_complements(library):
    """Compared per channel, not by position: the lit half of each scene also
    opens the shutters of the fixtures that have one, so the two scenes no
    longer carry the same number of values."""
    ws = Workspace.load(SHOW)
    generated = generate_dimmer_chases(ws, library)
    functions = _functions(ws.root)
    caps = {c.fixture.fixture_id: c for c in capabilities_of(ws.root, library)}

    def values_of(scene_id):
        result = {}
        for element in findall_local(functions[scene_id], "FixtureVal"):
            numbers = [int(n) for n in (element.text or "").split(",") if n != ""]
            result[int(element.attrib["ID"])] = dict(zip(numbers[::2], numbers[1::2]))
        return result

    first, second = (values_of(i) for i in generated.scene_ids)
    assert first.keys() == second.keys()
    for fixture_id, pairs in first.items():
        capability = caps[fixture_id]
        for offset in capability.offsets_for_role(roles.DIMMER):
            assert {pairs[offset], second[fixture_id][offset]} == {0, 255}


def test_the_lit_half_of_the_ping_pong_opens_its_shutter(library):
    """A fixture at full dimmer behind a closed shutter shows nothing.

    The BEAM 230W 7R used to be the example here. Since 2026-08-29 it is the
    counter-example instead: its dimmer is a mechanical blade, a chase that
    sweeps it draws half-moons rather than dips, and it is kept out of the
    chase entirely (`stepped_dimmer`).
    """
    ws = Workspace.load(SHOW)
    generated = generate_dimmer_chases(ws, library)
    functions = _functions(ws.root)
    caps = {c.fixture.fixture_id: c for c in capabilities_of(ws.root, library)}
    beams = {c.fixture.fixture_id for c in caps.values() if c.fixture.model == "BEAM 230W 7R"}
    assert beams

    seen_lit = False
    for scene_id in generated.scene_ids:
        pairs = {
            int(v.attrib["ID"]): dict(
                zip(
                    [int(n) for n in (v.text or "").split(",")][::2],
                    [int(n) for n in (v.text or "").split(",")][1::2],
                )
            )
            for v in findall_local(functions[scene_id], "FixtureVal")
        }
        assert not (beams & pairs.keys()), "a blade dimmer joined the ping-pong"
        for fixture_id, values in pairs.items():
            capability = caps[fixture_id]
            dimmers = capability.offsets_for_role(roles.DIMMER)
            shutters = shutter_open_pairs(capability)
            if not dimmers or not shutters:
                continue
            shutter, opening = shutters[0]
            if values[dimmers[0]] == 255:
                seen_lit = True
                assert values[shutter] == opening
            else:
                assert shutter not in values
    assert seen_lit


def test_a_strobe_value_lands_where_the_definition_says_it_strobes(library):
    """A labelled channel is driven inside its strobing range, never outside.

    A channel with no labels at all - the Vortex and panel speed channels,
    which *are* the strobe and say nothing else about themselves - is driven
    too (above zero), because leaving them out is how `Strobo ON` shipped
    strobing ten fixtures and skipping nine (2026-08-27). The hand-built show
    drove exactly those channels at 250/255 for years.
    """
    ws = Workspace.load(SHOW)
    generated = generate_strobe_effects(ws, library)
    functions = _functions(ws.root)
    assert generated.on_id is not None

    ranges = {}
    for capability in capabilities_of(ws.root, library):
        for offset, caps in capability.capabilities_for_role(roles.STROBE):
            ranges[(capability.fixture.fixture_id, offset)] = caps

    driven = bare = 0
    for element in findall_local(functions[generated.on_id], "FixtureVal"):
        fixture_id = int(element.attrib["ID"])
        numbers = [int(n) for n in (element.text or "").split(",") if n != ""]
        for offset, value in zip(numbers[0::2], numbers[1::2]):
            labels = ranges[(fixture_id, offset)]
            if not labels:
                assert value > 0, (fixture_id, offset, value)
                bare += 1
                continue
            hit = [c for c in labels if c.minimum <= value <= c.maximum]
            assert hit, (fixture_id, offset, value)
            assert "strobe" in hit[0].name.lower(), hit[0].name
            driven += 1
    assert driven >= 3  # the CromoWash, the MiN Wash and the beams
    assert bare >= 2  # the Vortex PARs and the panels


def test_the_console_strobes_are_held_shutter_scenes(library):
    """2026-09-02, cross-audit: the STROBO burst chasers alternated a white
    scene and a black one, and the black step - all Intensity channels, HTP -
    lost to any lit state: white / state-colour, never white / black. The two
    console strobes are held Flash scenes now, every strobe-capable channel at
    a rate and nothing else, fast on `F` and at the slow flash's pace on `T`
    (the `flash lento` rule refuses anything under 70% of the run).
    """
    from qlctool.generate.strobe_effects import FAST_FRACTION, MEDIUM_FRACTION
    from qlctool.strobe_speed import strobe_speed_pairs

    ws = Workspace.load(SHOW)
    generated = generate_strobe_effects(ws, library)
    functions = _functions(ws.root)
    expected = {
        c.fixture.fixture_id: (
            dict(strobe_speed_pairs(c, FAST_FRACTION)),
            dict(strobe_speed_pairs(c, MEDIUM_FRACTION)),
        )
        for c in capabilities_of(ws.root, library)
        if not c.is_smoke and strobe_speed_pairs(c, FAST_FRACTION)
    }
    assert MEDIUM_FRACTION >= 0.7

    for scene_id, which in ((generated.fast_id, 0), (generated.medium_id, 1)):
        scene = functions[scene_id]
        assert scene.attrib["Type"] == "Scene"
        written = {}
        for element in findall_local(scene, "FixtureVal"):
            numbers = [int(n) for n in (element.text or "").split(",") if n != ""]
            written[int(element.attrib["ID"])] = dict(zip(numbers[0::2], numbers[1::2]))
        assert written == {fixture_id: pair[which] for fixture_id, pair in expected.items()}


def test_a_channel_that_labels_its_open_position_no_strobe_is_not_read_as_one(library):
    """The name is a fallback, the preset is the meaning.

    The split CLB2.4 definition calls DMX 0 "No strobe" and marks it
    ShutterOpen, with the strobe itself on 1-255. Picking a range by name alone
    matched the first one and sent `Strobo ON` a zero - the single value that
    guarantees no strobe at all.
    """
    from qlctool.definition import Capability
    from qlctool.strobe_range import strobe_range

    ranges = (
        Capability(minimum=0, maximum=0, name="No strobe", preset="ShutterOpen"),
        Capability(minimum=1, maximum=255, name="Strobe, slow to fast", preset="StrobeSlowToFast"),
    )

    chosen = strobe_range(ranges)

    assert chosen is not None and chosen.minimum == 1
