"""Variety on top of the family split: rotation and serial cascades.

All 23 EFX ran Rotation=0 and Parallel propagation - every shape an axis-aligned
clone of the others (Codex A6). A Serial EFX delays each fixture by
`loopDuration/(fixtureCount+1)*serialNumber` (efxfixture.cpp:380-386), which
turns a plain shape into a cascade down the row for free. Two new figures use
it - `Ola Suave` (washes, Line) and `Cascada Beams` (beams, Circle, Rotation
45) - and two existing beam shapes get a rotation so they stop tracing the same
axes as their wash counterparts.
"""

from pathlib import Path

import pytest

from qlctool.checks.run import check_workspace
from qlctool.generate.movement_families import generate_movement_families
from qlctool.library import FixtureLibrary
from qlctool.monitor_positions import house_right_fixture_ids
from qlctool.skeleton import strip_to_skeleton
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, iter_local

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "Vibra.qxw"


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


def _efx_by_name(root):
    return {
        f.attrib["Name"]: f for f in iter_local(root, "Function") if f.attrib.get("Type") == "EFX"
    }


def _generated(library):
    ws = strip_to_skeleton(Workspace.load(SHOW))
    mirrored = house_right_fixture_ids(ws.root)
    generate_movement_families(ws, library, mirrored_ids=mirrored)
    return ws


def test_ola_suave_is_a_serial_line_wash(library):
    ws = _generated(library)
    functions = _efx_by_name(ws.root)

    assert "Ola Suave" in functions
    ola = functions["Ola Suave"]
    assert find_local(ola, "Algorithm").text == "Line"
    assert find_local(ola, "PropagationMode").text == "Serial"
    # Slow, the Suave duration class (28000ms family), not the faster Wash one.
    assert int(find_local(ola, "Speed").attrib["Duration"]) == 28000


def test_cascada_beams_is_a_serial_rotated_circle(library):
    ws = _generated(library)
    functions = _efx_by_name(ws.root)

    assert "Cascada Beams" in functions
    cascada = functions["Cascada Beams"]
    assert find_local(cascada, "Algorithm").text == "Circle"
    assert find_local(cascada, "PropagationMode").text == "Serial"
    assert int(find_local(cascada, "Rotation").text) == 45


def test_beam_diamond_and_leaf_break_the_axis_alignment(library):
    ws = _generated(library)
    functions = _efx_by_name(ws.root)

    assert "Beam Diamante" in functions
    assert int(find_local(functions["Beam Diamante"], "Rotation").text) == 90
    assert "Beam Hoja" in functions
    assert int(find_local(functions["Beam Hoja"], "Rotation").text) == 45

    # The pre-existing wash shapes are untouched by this task.
    assert int(find_local(functions["Wash Diamante"], "Rotation").text) == 0
    assert int(find_local(functions["Wash Hoja"], "Rotation").text) == 0


def test_the_far_side_still_runs_the_new_figures_backwards(library):
    """The mirrored house-right logic must survive the new figures too - a
    Serial or rotated EFX is still an EFX with a per-fixture Direction."""
    ws = _generated(library)
    mirrored = house_right_fixture_ids(ws.root)
    functions = _efx_by_name(ws.root)

    for name in ("Ola Suave", "Cascada Beams", "Beam Diamante", "Beam Hoja"):
        function = functions[name]
        checked = 0
        for fixture in findall_local(function, "Fixture"):
            fixture_id = int(find_local(fixture, "ID").text)
            direction = find_local(fixture, "Direction").text
            expected = "Backward" if fixture_id in mirrored else "Forward"
            assert direction == expected, f"{name}, fixture {fixture_id}"
            checked += 1
        assert checked, name


def test_movement_families_still_pass_the_mixed_optics_rule(library):
    """One optics family per EFX - adding cascades must not blur that line."""
    ws = _generated(library)
    findings = [
        f for f in check_workspace(ws, library) if f.rule == "familias de movimiento mezcladas"
    ]
    assert not findings, "\n".join(str(f) for f in findings)


def test_every_shipped_efx_still_has_the_family_shapes(library):
    """No pre-existing figure lost its shape or its family in the process."""
    ws = _generated(library)
    functions = _efx_by_name(ws.root)
    for name in ("Wash Circulo", "Beam Circulo", "Suave Circulo"):
        assert name in functions
