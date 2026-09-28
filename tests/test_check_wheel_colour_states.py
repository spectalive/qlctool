"""The checks, and one test per bug that has actually happened in the room.

Split by topic out of the original `test_check.py` (over the codeality
test-file line cap): this file covers the 2026-09-22 wheel-colour rulings -
a spinning wheel, white back on the rotation, the multicolour wheel bleeding
into a state, and complementary colours split across one wash.
"""

import pytest
from fixture_val_pairs import fixture_val_pairs as _pairs_of
from functions_by_id_of_workspace import functions_by_id_of_workspace as _functions_by_id
from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions
from lxml import etree
from named_show import named_show as _show
from write_fixture_val_pairs import write_fixture_val_pairs as _write_pairs

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.checks.check_workspace import check_workspace
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary

BEAMS = (20, 21, 22, 23)


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


def test_a_rig_colour_that_spins_the_beams_wheel_instead_of_naming_one(library):
    """2026-08-29: "las 7R no se abren del todo, están como una media luna".

    Live under AUTO, nothing else pressed. Nothing was closed: two of the
    twenty steps of the colour clock - `Rig Multicolor 1` and `Rig Multicolor
    2` - put the beams' colour wheel at 186, inside its rotation range and near
    the slow end. A turning wheel spends its time between detents, and a
    2-degree beam looking through a split wheel shows half of one colour and
    half of the next. Put the scroll value back and the rule must bite.
    """
    workspace = _show()
    functions = _functions(workspace)
    scene = functions["Rig Multicolor 1"]
    wheel = {
        capability.fixture.fixture_id: capability.wheel_for_role(roles.COLOR_MACRO)[0]
        for capability in capabilities_of(workspace.root, library)
        if capability.fixture.fixture_id in BEAMS
    }
    for value in findall_local(scene, "FixtureVal"):
        fixture_id = int(value.attrib["ID"])
        if fixture_id not in wheel:
            continue
        value.text = f"{wheel[fixture_id]},186"

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "rueda de color girando"
    ]
    assert findings, "a rig colour spinning the beams' wheel went unnoticed"
    assert "Rig Multicolor 1" in {f.function for f in findings}
    assert all("BEAM" in fixture for f in findings for fixture in f.fixtures)


def test_2026_09_22_white_back_on_the_wheel(library):
    """ "Las luces blancas en las ruedas de colores automáticas no ... en
    directo se ve todo iluminado y queda horrible" (owner, 2026-09-22).

    Every rotation used to step white - eighteen palette colours, white the
    eighteenth. Paint one step of the rig wheel white again, RGB all equal
    and lit on every fixture it writes, and the rule must bite.
    """
    workspace = _show()
    functions = _functions(workspace)
    scene = functions["Rig Rojo"]
    caps = {c.fixture.fixture_id: c for c in capabilities_of(workspace.root, library)}
    for value in findall_local(scene, "FixtureVal"):
        capability = caps[int(value.attrib["ID"])]
        pairs = _pairs_of(value)
        for role in (roles.RED, roles.GREEN, roles.BLUE):
            for offset in capability.offsets_for_role(role):
                if offset in pairs:
                    pairs[offset] = 255
        _write_pairs(value, pairs)

    findings = [f for f in check_workspace(workspace, library) if f.rule == "blanco en la rueda"]
    assert findings, "a white step on the colour wheel went unnoticed"
    assert {f.function for f in findings} == {"Rueda Colores"}
    assert all("Rig Rojo" in f.message for f in findings)


def test_2026_09_22_the_multicolour_deal_back_in_the_state_wheel(library):
    """ "Los colores siguen siendo una feria ... un modo multicolor solo por
    si acaso, y los otros modos con colores sutiles, como mucho 2 mezclas"
    (owner, 2026-09-22).

    The wild steps rode `Rueda Colores` - AUTO's own wheel - until that
    evening. Put one back and the rule must bite: a state may rotate two
    colours at most, and the multicolour wheel is a button, not a state.
    """
    workspace = _show()
    functions = _functions(workspace)
    by_id = _functions_by_id(workspace)
    wheel = functions["Rueda Colores"]
    wild = next(
        step
        for step in findall_local(functions["Rueda Multicolor"], "Step")
        if by_id[step.text].attrib["Name"].startswith("Rig Multicolor 1")
    )
    step = etree.SubElement(wheel, "Step")
    step.text = wild.text
    step.attrib["Number"] = str(len(findall_local(wheel, "Step")) - 1)

    findings = [
        f
        for f in check_workspace(workspace, library)
        if f.rule == "mas de dos colores en un estado"
    ]
    assert findings, "a multicolour step on a state's wheel went unnoticed"
    assert {f.function for f in findings} == {"Rueda Colores"}
    # The multicolour wheel itself is a layer somebody presses: not judged.
    assert not any(f.function == "Rueda Multicolor" for f in findings)


def test_2026_09_22_complementary_colours_split_across_one_wash(library):
    """ "Tiene que haber alguna regla o recomendaciones sobre eso, cuales
    casan mejor o usan los prods" (owner, 2026-09-22).

    There is: complementary colours on one surface desaturate each other
    towards white, so they belong between roles and never alternating
    inside one group. The mix wheels stepped "Azul / Amarillo PAR" thirty
    times a night. Put the yellow half of a split on cyan - red's opposite -
    and the rule must bite; the neighbouring pair it replaces must not.
    """
    workspace = _show()
    functions = _functions(workspace)
    scene = functions["Rojo / Amarillo PAR"]
    caps = {c.fixture.fixture_id: c for c in capabilities_of(workspace.root, library)}
    for value in findall_local(scene, "FixtureVal"):
        capability = caps[int(value.attrib["ID"])]
        pairs = _pairs_of(value)
        greens = [pairs.get(o, 0) for o in capability.offsets_for_role(roles.GREEN)]
        if not greens or max(greens) == 0:
            continue  # the red half stays red
        for role, level in ((roles.RED, 0), (roles.GREEN, 255), (roles.BLUE, 255)):
            for offset in capability.offsets_for_role(role):
                if offset in pairs:
                    pairs[offset] = level
        _write_pairs(value, pairs)

    findings = [
        f
        for f in check_workspace(workspace, library)
        if f.rule == "complementarios en un mismo lavado"
    ]
    assert findings, "two opposite colours alternating on one wash went unnoticed"
    assert {f.function for f in findings} == {"Rojo / Amarillo PAR"}
