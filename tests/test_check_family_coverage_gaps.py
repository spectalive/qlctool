"""The checks, and one test per bug that has actually happened in the room.

Split by topic out of the original `test_check.py` (over the codeality
test-file line cap): this file covers 2026-09-22 owner review findings where
one optics family (colour animation, dimmer sweep, figure, tinted white) left
another family or fixture out of its own coverage.
"""

import pytest
from fixture_val_pairs import fixture_val_pairs as _pairs_of
from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions
from named_show import named_show as _show
from write_fixture_val_pairs import write_fixture_val_pairs as _write_pairs

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.checks.check_workspace import check_workspace
from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.iter_local import iter_local
from qlctool.localname import localname


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


def test_2026_09_22_a_tint_washed_out_by_its_own_white_share(library):
    """2026-09-22, owner reviewing the programme: "charla y blanco son lo
    mismo", and the colour hits came out "mezclados con blanco". The
    white-emitter fix of 2026-09-02 wrote min(r,g,b) to the White channel and
    left red, green and blue untouched, so the achromatic part of every tinted
    colour was emitted twice - `Luz Charla`, the warm (255, 214, 170), arrived
    as white. Reproduced by putting the additive values back on one Mini Led.
    """
    workspace = _show()
    caps = {c.fixture.fixture_id: c for c in capabilities_of(workspace.root, library)}
    tinted = next(
        c
        for c in caps.values()
        if c.offsets_for_role(roles.WHITE) and c.offsets_for_role(roles.RED)
    )
    warm = (255, 214, 170)
    for value in findall_local(_functions(workspace)["Luz Charla Base"], "FixtureVal"):
        if int(value.attrib["ID"]) != tinted.fixture.fixture_id:
            continue
        pairs = _pairs_of(value)
        for role, level in zip((roles.RED, roles.GREEN, roles.BLUE), warm, strict=True):
            for offset in tinted.offsets_for_role(role):
                pairs[offset] = level
        for offset in tinted.offsets_for_role(roles.WHITE):
            pairs[offset] = min(warm)
        _write_pairs(value, pairs)

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "blanco pagado dos veces"
    ]
    assert findings, "a tint emitted twice went unnoticed"
    assert "Luz Charla Base" in {f.function for f in findings}
    named = {name for f in findings for name in f.fixtures}
    assert tinted.fixture.name in named


def test_2026_09_22_a_rainbow_that_leaves_the_beams_on_one_colour(library):
    """2026-09-22, owner reviewing the programme: "el arcoiris no funciona con
    los beam, no hace el color arcoiris". Both rainbows are relative EFX in RGB
    mode built over "every RGB head", and `generate_rainbow_efx.py` finds no red channel
    on a 7R, so the spectrum swept the room with the four beams parked on
    whatever detent the state had left. Reproduced by taking the beams' own
    rainbow-spin layer back out of the rainbow's collection.
    """
    workspace = _show()
    functions = _functions(workspace)
    rainbow = functions["Arcoiris Simultaneo"]
    assert rainbow.attrib["Type"] == "Collection", "the rainbow lost its beam layer"
    spin = functions["Color Beam - Arcoiris (capa)"]
    steps = [s for s in findall_local(rainbow, "Step") if s.text == spin.attrib["ID"]]
    assert steps, "the rainbow collection no longer carries the spin layer"
    for step in steps:
        rainbow.remove(step)

    findings = [
        f
        for f in check_workspace(workspace, library)
        if f.rule == "animacion de color sin la rueda"
    ]
    assert findings, "a rainbow that skips the wheel-coloured fixtures went unnoticed"
    assert all(name.startswith("BEAM") for f in findings for name in f.fixtures)


def test_2026_09_22_an_intensity_sweep_no_tap_can_reach(library):
    """2026-09-22, owner reviewing the programme: "los barridos de intensidad
    van a su bola". Both sweeps are Collections of one dimmer-mode EFX per
    fixture family, and the tempo dial only ever listed functions that carry a
    speed of their own - a Collection does not - so the sweeps kept their
    milliseconds whatever the room's tap said. Reproduced by dropping their
    EFX from the dial again.
    """
    workspace = _show()
    names = {
        int(f.attrib["ID"]): f.attrib.get("Name", "")
        for f in workspace.engine
        if localname(f) == "Function" and "ID" in f.attrib
    }
    console = find_local(workspace.root, "VirtualConsole")
    dial = next(iter_local(console, "SpeedDial"))
    dropped = 0
    for function in findall_local(dial, "Function"):
        name = names.get(int((function.text or "0").strip()), "")
        if name.startswith("Dimmer Chase"):
            dial.remove(function)
            dropped += 1
    assert dropped, "the sweeps are no longer on the tempo dial"

    findings = [f for f in check_workspace(workspace, library) if f.rule == "ritmo sin reloj"]
    assert findings, "an intensity sweep outside every dial went unnoticed"
    assert all("Dimmer Chase" in f.message for f in findings)


def test_2026_09_22_a_figure_that_leaves_the_beams_standing(library):
    """2026-09-22, owner reviewing the programme: "algunos movimientos de cabeza
    no incluyen las beam". A figure button is the per-family EFX under one name,
    and `Square` and `Lissajous` were wash-only shapes, so those two buttons
    moved the six washes and left the four 7R standing - nothing in the file
    said a family was missing. Reproduced by taking the beams' half of a figure
    back out of its collection.
    """
    workspace = _show()
    functions = _functions(workspace)
    figure = functions["Movimiento Cuadrado"]
    by_id = {
        f.attrib["ID"]: f
        for f in workspace.engine
        if localname(f) == "Function" and "ID" in f.attrib
    }
    beam_parts = [
        step
        for step in findall_local(figure, "Step")
        if "Beam" in by_id[step.text].attrib.get("Name", "")
    ]
    assert beam_parts, "the square figure no longer carries a beam EFX"
    for step in beam_parts:
        figure.remove(step)

    findings = [
        f
        for f in check_workspace(workspace, library)
        if f.rule == "figura que deja cabezas quietas"
    ]
    assert findings, "a figure that moves one optics family only went unnoticed"
    assert all(name.startswith("BEAM") for f in findings for name in f.fixtures)
