"""The checks, and one test per bug that has actually happened in the room.

Split by topic out of the original `test_check.py` (over the codeality
test-file line cap): this file covers the beams' movement - parked movers,
mid-travel figures, blade dimmers, the audience window - and a held smoke pump.
"""

import pytest
from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions
from named_show import named_show as _show
from rig_root import RIG_ROOT

from qlctool import roles
from qlctool.audience_windows import BEAM_WINDOW
from qlctool.capabilities_of import capabilities_of
from qlctool.checks.check_workspace import check_workspace
from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.generate.build_canonical_show import build_canonical_show
from qlctool.workspace import Workspace

REPO = RIG_ROOT
BEAMS = (20, 21, 22, 23)


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


def test_a_level_of_the_cycle_that_parks_half_the_movers(library):
    """2026-08-29: "las 7R ... no se mueven", again with only AUTO pressed.

    `Nivel Ambiente` is the first and longest step of `Ciclo Energia`: its
    `Movimientos Suaves` Collection starts both slow chasers. Swap the beams'
    slow rotation back for a static fan and the rule must bite.
    """
    workspace = Workspace.load(REPO / "QLC+ Setups" / "DeluxeEventos2.qxw")
    build_canonical_show(workspace, library, with_layout=False)
    functions = _functions(workspace)
    by_name = {
        name: int(function.attrib["ID"])
        for name, function in functions.items()
        if function.attrib.get("ID")
    }
    level = functions["Movimientos Suaves"]
    slow_beams = str(by_name["Suaves Beams"])
    fan = str(by_name["Beams Abanico"])
    swapped = False
    for step in findall_local(level, "Step"):
        if (step.text or "").strip() == slow_beams:
            step.text = fan
            swapped = True
    assert swapped, "`Movimientos Suaves` no longer moves the beams at all"

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "cabezas paradas en el ciclo"
    ]
    assert findings, "a cycle level parking the beams went unnoticed"
    assert "Nivel Ambiente" in {f.function for f in findings}
    assert all("BEAM" in fixture for f in findings for fixture in f.fixtures)


def test_a_split_movement_is_not_a_block_that_parks_the_beams(library):
    """2026-09-02: the wash figures became pairs of EFX, and the rule bit.

    The Mini Led Moving Head's channels 9-16 were settled off three agreeing
    OEM charts, which put its fine channels at 14 and 15 - not beside the
    coarse ones - so every wash figure is now a 16-bit EFX and an 8-bit EFX
    under one Collection (`keeps_16bit`). As a step of the washes' chaser that
    Collection moves the washes and not the beams, exactly as the single EFX
    did, and the beams' chaser beside it moves the beams. The rule must read
    it as one movement, not as a block of the cycle parking four 7R - while a
    block that mixes a static scene into the step still bites (the test
    above).
    """
    workspace = _show()
    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "cabezas paradas en el ciclo"
    ]
    assert not findings, [f.function for f in findings]
    functions = _functions(workspace)
    pairs = [
        name
        for name, function in functions.items()
        if function.attrib.get("Type") == "Collection" and (name or "").startswith("Wash ")
    ]
    assert pairs, "the wash figures are no longer split into EFX pairs"


def test_a_beam_figure_centred_on_mid_travel(library):
    """2026-08-29: "está todo el rato haciendo un circulo pequeño en el suelo".

    Every movement EFX carried QLC+'s own axis default - tilt offset 127, the
    raw middle of the channel - because nothing had ever overridden it. Mid
    travel is not a place: on the 7R it is the floor, on the washes the wall
    behind the stage. Put the default back on a beam figure and the rule must
    bite.
    """
    workspace = _show()
    functions = _functions(workspace)
    efx = functions["Beam Suave Circulo"]
    axis = next(a for a in findall_local(efx, "Axis") if a.attrib.get("Name") == "Y")
    offset = find_local(axis, "Offset")
    assert offset.text != "127", "the beams' figure is aimed at mid travel again"
    offset.text = "127"

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "movimiento sin apuntar"
    ]
    assert findings, "a beam figure centred on mid travel went unnoticed"
    assert "Beam Suave Circulo" in {f.function for f in findings}
    assert all("BEAM" in fixture for f in findings for fixture in f.fixtures)


def test_a_fraction_written_to_a_blade_dimmer(library):
    """2026-08-29, the owner reading the desk during the show: "el canal 7 de
    cada 7R está a la mitad en vez de abierto del todo".

    Channel 7 is the BEAM 230W 7R's dimmer, and on a 7R that is a mechanical
    blade, not a fader. `Intensidad Ambiente` wrote 110 to every dimmer in the
    rig and the quiet level held it for four minutes, so the blade sat half
    across the lens: "están como una media luna". Put the fraction back and the
    rule must bite.
    """
    workspace = _show()
    functions = _functions(workspace)
    scene = functions["Intensidad Ambiente"]
    dimmers = {
        capability.fixture.fixture_id: capability.offsets_for_role(roles.DIMMER)
        for capability in capabilities_of(workspace.root, library)
        if capability.fixture.fixture_id in BEAMS
    }
    for value in findall_local(scene, "FixtureVal"):
        fixture_id = int(value.attrib["ID"])
        if fixture_id not in dimmers:
            continue
        numbers = [int(n) for n in (value.text or "").split(",") if n != ""]
        pairs = dict(zip(numbers[0::2], numbers[1::2], strict=True))
        for offset in dimmers[fixture_id]:
            pairs[offset] = 110
        value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))

    findings = [f for f in check_workspace(workspace, library) if f.rule == "dimmer a medias"]
    assert findings, "a fraction on a blade dimmer went unnoticed"
    assert "Intensidad Ambiente" in {f.function for f in findings}
    assert all("BEAM" in fixture for f in findings for fixture in f.fixtures)


def test_a_dimmer_efx_sweeping_a_blade_dimmer(library):
    """The same fault in motion: an EFX in Dimmer mode over the blade sweeps it,
    so most of every pass is a half-moon rather than a dip (2026-08-29).
    """
    workspace = _show()
    efx = _functions(workspace)["Dimmer Chase CromoWash100"]
    member = findall_local(efx, "Fixture")[0]
    find_local(member, "ID").text = str(BEAMS[0])

    findings = [f for f in check_workspace(workspace, library) if f.rule == "dimmer a medias"]
    assert findings, "a dimmer EFX sweeping a blade went unnoticed"
    assert any("BEAM" in fixture for f in findings for fixture in f.fixtures)


def test_a_beam_figure_that_leaves_the_audience(library):
    """2026-08-29: the aim was guessed twice and was wrong twice - the beams
    drew a circle on the floor, then pointed at the wall behind.

    It ended with the owner putting BEAM 230W 7R #1 on the desk and sending the
    corners of where the people are: "eso son los rangos del publico, todo lo
    fuera de eso ya apunta a fuera". With the window written down the question
    is arithmetic. Grow a figure past it and the rule must bite.
    """
    workspace = _show()
    efx = _functions(workspace)["Beam Circulo"]
    height = find_local(efx, "Height")
    inside = int(height.text)
    assert BEAM_WINDOW.holds(
        int(
            find_local(
                next(a for a in findall_local(efx, "Axis") if a.attrib.get("Name") == "Y"), "Offset"
            ).text
        ),
        inside,
        "tilt",
    ), "the shipped beam figure already leaves the audience window"
    height.text = str(inside + 40)

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "figura fuera del publico"
    ]
    assert findings, "a beam figure sweeping out of the room went unnoticed"
    assert "Beam Circulo" in {f.function for f in findings}
    assert all("BEAM" in fixture for f in findings for fixture in f.fixtures)


def test_a_held_pump_on_a_channel_qlcplus_never_resets(library):
    """The rest of the same night. Holding the button did not stop it either:
    "le doy y no para de echar todo el rato".

    QLC+ rebuilds the universe from the running faders every cycle but only
    resets the **Intensity** group first (`Universe::processFaders` ->
    `zeroIntensityChannels`); every other group keeps its last value. The Fog
    channel was declared in Effect, so releasing the flash removed the flash's
    fader and changed nothing. Put the pump back outside the reset group and
    the rule must bite.
    """
    from dataclasses import replace

    workspace = _show()
    broken = FixtureLibrary.load()
    definition = broken.get("Generic", "LED Spray Fog")
    assert definition is not None, "the vertical fog machines left the library"
    pump = definition.channels["Fog"]
    assert pump.group.lower() == "intensity", "the pump left the reset group"
    definition.channels["Fog"] = replace(pump, group="Effect")

    findings = [f for f in check_workspace(workspace, broken) if f.rule == "humo pegado"]
    assert findings, "a held pump QLC+ never resets went unnoticed"
    assert any("Humo" in fixture for f in findings for fixture in f.fixtures)
