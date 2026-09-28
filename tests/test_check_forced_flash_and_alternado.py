"""The checks, and one test per bug that has actually happened in the room.

Split by topic out of the original `test_check.py` (over the codeality
test-file line cap): this file covers `forced_flash_triggers`' determinism,
a forced flash closing the MiN Wash or halving a dimmer, and the `Alternado`
twin-movement figures matching their plain counterpart's rigged heads.
"""

import copy

import pytest
from efx_under import efx_under as _efx_under
from fixture_val_pairs import fixture_val_pairs as _pairs_of
from functions_by_id_of_workspace import functions_by_id_of_workspace as _functions_by_id
from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions
from named_show import named_show as _show
from shipped_graphs import shipped_graphs as _shipped_graphs
from write_fixture_val_pairs import write_fixture_val_pairs as _write_pairs

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.checks.check_workspace import check_workspace
from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


def _lower_in_flash(workspace, library, pick, level):
    """Write `level` on the offsets `pick(capability)` gives, in `Flash 100%`."""
    scene = _functions(workspace)["Flash 100%"]
    caps = {c.fixture.fixture_id: c for c in capabilities_of(workspace.root, library)}
    lowered = set()
    for value in findall_local(scene, "FixtureVal"):
        capability = caps[int(value.attrib["ID"])]
        offsets = pick(capability)
        if not offsets:
            continue
        pairs = _pairs_of(value)
        for offset in offsets:
            pairs[offset] = level
        _write_pairs(value, pairs)
        lowered.add(capability.fixture.name)
    return lowered


def _heads_of(efx):
    """(fixture id, direction, start offset) per head, in the EFX's own order."""
    return [
        (
            int(find_local(f, "ID").text),
            find_local(f, "Direction").text,
            int(find_local(f, "StartOffset").text),
        )
        for f in findall_local(efx, "Fixture")
    ]


def test_2026_09_26_forced_flash_triggers_is_deterministic_across_calls():
    """2853e38: `forced` used to key its forced-LTP buttons by `id(button)`, a
    transient object's identity - once the loop moved on, CPython was free to
    reuse that address for the very next button, so a pad `Input` could match
    the wrong function depending on garbage-collection timing rather than on
    which widget it is actually bound to. On the shipped `Vibra.qxw`, keying
    by `id()` picks up a handful of such phantom `("pad", ...)` triggers, and
    which ones differs from call to call. Element identity carries no such
    risk, so repeated calls against the same, unchanged workspace must always
    return exactly the same mapping.
    """
    import gc

    from qlctool.checks.forced_flash_triggers import forced_flash_triggers

    workspace = _show("Vibra.qxw")
    first = forced_flash_triggers(workspace.root)
    assert first
    for _ in range(20):
        gc.collect()
        assert forced_flash_triggers(workspace.root) == first


def test_2026_09_26_a_forced_flash_that_closes_the_min_wash(library):
    """2026-09-26, round 1 review (I1): the MiN Wash's only intensity is its
    Dimmer/Strobe channel, and 0 there is "Closed". A forced flash writing it
    0 blacks out what the level and the work light give them - the D1 trap on
    a strobe-role channel. Unlike a PAR's "no strobe" 0, it must bite.
    """
    from qlctool.checks.rule_flash_forced_zero import RULE_ID

    workspace = _show()
    closed = _lower_in_flash(
        workspace,
        library,
        lambda c: c.offsets_for_role(roles.STROBE) if not c.offsets_for_role(roles.DIMMER) else [],
        0,
    )
    assert {"MiN Wash #1", "MiN Wash #2"} <= closed
    findings = [f for f in check_workspace(workspace, library) if f.rule_id == RULE_ID]
    assert [f.function for f in findings] == ["Flash 100%"]
    assert {"MiN Wash #1", "MiN Wash #2"} <= set(findings[0].fixtures)


def test_2026_09_26_a_forced_flash_that_halves_a_dimmer(library):
    """2026-09-26, round 1 review (M3): a forced flash cuts a dimmer by writing
    it lower than a state holds it, not only by writing it 0. Half the
    dimmers of `Flash 100%` and the rule must name those fixtures.
    """
    from qlctool.checks.rule_flash_forced_zero import RULE_ID

    workspace = _show()
    halved = _lower_in_flash(
        workspace,
        library,
        lambda c: [] if c.is_smoke else c.offsets_for_role(roles.DIMMER),
        128,
    )
    assert halved
    findings = [f for f in check_workspace(workspace, library) if f.rule_id == RULE_ID]
    assert [f.function for f in findings] == ["Flash 100%"]
    assert set(findings[0].fixtures) == halved


def test_2026_09_26_alternado_equals_the_default_on_the_rigged_heads(library):
    """2026-09-26, en-sala DMX audit (item 2): the seven `Alternado` buttons
    moved the four 7R and the two MAC WASH exactly as the plain buttons did.
    "Every other head" came from patch order, which on this rig is the
    house-right pair the default already reverses, and the washes' every
    other head and phase slot went to spares. Ruling D5: the beams alternate
    by stage order (x 20, 22, 23, 21 - reverse 22 and 21), and two rigged
    washes run both Forward half a figure apart. Give `Movimiento Circulo
    Alternado` the default's heads back and the rule must pair the buttons.
    """
    from qlctool.checks.rule_twin_movement import RULE_ID, check_twin_movement

    for name, graph, _ in _shipped_graphs(library):
        assert check_twin_movement(graph, _show(name).root) == [], name

    workspace = _show("Vibra.qxw")
    functions = _functions(workspace)
    beams = _heads_of(functions["Beam Circulo Alternado"])
    assert {i for i, direction, _ in beams if direction == "Backward"} == {22, 21}
    assert [i for i, _, _ in beams] == [20, 22, 23, 21]
    washes = _heads_of(_efx_under(_functions_by_id(workspace), functions["Wash Circulo"])[0])
    alternate = _heads_of(
        _efx_under(_functions_by_id(workspace), functions["Wash Circulo Alternado"])[0]
    )
    assert washes[:2] == [(33, "Forward", 0), (34, "Backward", 180)]
    assert alternate[:2] == [(33, "Forward", 0), (34, "Forward", 180)]

    by_id = _functions_by_id(workspace)
    plain = _efx_under(by_id, functions["Movimiento Circulo"])
    twin = _efx_under(by_id, functions["Movimiento Circulo Alternado"])
    for source, target in zip(plain, twin, strict=True):
        for head in findall_local(target, "Fixture"):
            target.remove(head)
        for head in findall_local(source, "Fixture"):
            target.append(copy.deepcopy(head))
    findings = [f for f in check_workspace(workspace, library) if f.rule_id == RULE_ID]
    assert [(f.function, f.fields["twin"]) for f in findings] == [
        ("Jugar · Movimiento Circulo Alternado", "Jugar · Movimiento Circulo")
    ]
    assert set(findings[0].fixtures) == {
        "BEAM 230W 7R #1",
        "BEAM 230W 7R #2",
        "BEAM 230W 7R #3",
        "BEAM 230W 7R #4",
        "MAC WASH 1915Z #1",
        "MAC WASH 1915Z #2",
    }
