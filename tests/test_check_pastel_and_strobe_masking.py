"""The checks, and one test per bug that has actually happened in the room.

Split by topic out of the original `test_check.py` (over the codeality
test-file line cap): this file covers the 2026-09-26 en-sala DMX audit -
a pastel's white share dropped by a second RGB-only fixture, a strobe the
room's HTP level outbids, a forced flash cutting the smoke, and a bank key
that skips fixtures outside every group.
"""

import pytest
from fixture_val_pairs import fixture_val_pairs as _pairs_of
from functions_by_id_of_workspace import functions_by_id_of_workspace as _functions_by_id
from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions
from lxml import etree
from named_show import named_show as _show
from shipped_graphs import shipped_graphs as _shipped_graphs
from twin_scene import twin_scene as _twin_scene
from write_fixture_val_pairs import write_fixture_val_pairs as _write_pairs

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.checks.build_show_graph import build_show_graph
from qlctool.checks.check_workspace import check_workspace
from qlctool.checks.group_fixtures import group_fixtures
from qlctool.checks.room_states import room_states
from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.fog_offsets import fog_offsets
from qlctool.iter_local import iter_local

SHOWS = ("Vibra.qxw", "Vibra-beats.qxw", "Vibra-split.qxw")


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


def _drop_pars_from_key(workspace, key, pars):
    """Take `pars` out of the one scene `key` presses that holds them."""
    from qlctool.checks.forced_flash_triggers import forced_flash_triggers

    by_id = _functions_by_id(workspace)
    holders = [
        by_id[str(function_id)]
        for function_id in forced_flash_triggers(workspace.root)[("key", key)]
        if pars
        <= {int(v.attrib["ID"]) for v in findall_local(by_id[str(function_id)], "FixtureVal")}
    ]
    assert len(holders) == 1, f"the PARs belong in exactly one scene of key {key}"
    for value in list(findall_local(holders[0], "FixtureVal")):
        if int(value.attrib["ID"]) in pars:
            holders[0].remove(value)
    return holders[0]


def test_2026_09_26_a_pastel_that_loses_its_white_on_rgb_only_fixtures(library):
    """2026-09-26, en-sala DMX audit (items 1 and 9): `Rig Pastel Rojo` gave
    twenty-three fixtures (115, 0, 0) and `Luz Charla` a brown (85, 44, 0).
    `rgbw_split` ran once per scene, so the white share left red, green and
    blue on every fixture and reached a White emitter only where there was
    one. Put the remainder back on one RGB-only fixture of each scene - what
    the old generator wrote - and the rule must name it.
    """
    from qlctool.checks.rule_white_share_dropped import RULE_ID, check_white_share_dropped

    for name, graph, groups in _shipped_graphs(library):
        assert check_white_share_dropped(graph, groups) == [], name

    workspace = _show()
    functions = _functions(workspace)
    caps = {c.fixture.fixture_id: c for c in capabilities_of(workspace.root, library)}
    rgb = (roles.RED, roles.GREEN, roles.BLUE)
    broken: dict[str, str] = {}
    for scene_name in ("Rig Pastel Rojo", "Luz Charla Base"):
        values = list(findall_local(functions[scene_name], "FixtureVal"))
        emitter = next(v for v in values if caps[int(v.attrib["ID"])].offsets_for_role(roles.WHITE))
        emitter_caps = caps[int(emitter.attrib["ID"])]
        pairs = _pairs_of(emitter)
        # The emitter's own RGB is the split's remainder: its white share went
        # to its White channel.
        remainder = [max(pairs[o] for o in emitter_caps.offsets_for_role(r)) for r in rgb]
        assert max(pairs[o] for o in emitter_caps.offsets_for_role(roles.WHITE)) > 0
        assert len(set(remainder)) > 1, "the scene has no tint left to split"
        plain = next(
            v
            for v in values
            if not caps[int(v.attrib["ID"])].offsets_for_role(roles.WHITE)
            and caps[int(v.attrib["ID"])].offsets_for_role(roles.RED)
        )
        plain_caps = caps[int(plain.attrib["ID"])]
        pairs = _pairs_of(plain)
        for role, level in zip(rgb, remainder, strict=True):
            for offset in plain_caps.offsets_for_role(role):
                pairs[offset] = level
        _write_pairs(plain, pairs)
        broken[scene_name] = plain_caps.fixture.name

    findings = {
        f.function: f.fixtures for f in check_workspace(workspace, library) if f.rule_id == RULE_ID
    }
    assert set(findings) == set(broken)
    for scene_name, fixture in broken.items():
        assert findings[scene_name] == (fixture,)


def test_2026_09_26_a_pastel_split_across_the_scenes_of_one_step(library):
    """2026-09-26, en-sala DMX audit (items 1 and 9), the chaser half: a step
    that starts one scene for the White emitters and another for the rest
    loses the white share just the same, and neither scene shows it alone.
    Split `Rig Pastel Rojo` that way, with the remainder on one RGB-only
    fixture, run both from a Collection stepped by a chaser, and the rule
    must name that fixture on the step.
    """
    from qlctool.checks.rule_white_share_dropped import RULE_ID
    from qlctool.functions.build_chaser import build_chaser
    from qlctool.functions.build_collection import build_collection
    from qlctool.next_function_id import next_function_id

    workspace = _show()
    functions = _functions(workspace)
    caps = {c.fixture.fixture_id: c for c in capabilities_of(workspace.root, library)}
    emitters = _twin_scene(workspace, functions, "Rig Pastel Rojo", "Pastel Emisores")
    rest = _twin_scene(workspace, functions, "Rig Pastel Rojo", "Pastel Resto")
    remainder = None
    for value in list(findall_local(emitters, "FixtureVal")):
        capability = caps[int(value.attrib["ID"])]
        if not capability.offsets_for_role(roles.WHITE):
            emitters.remove(value)
        elif remainder is None:
            pairs = _pairs_of(value)
            remainder = [
                max(pairs[o] for o in capability.offsets_for_role(r))
                for r in (roles.RED, roles.GREEN, roles.BLUE)
            ]
    plain = next(
        v
        for v in findall_local(rest, "FixtureVal")
        if caps[int(v.attrib["ID"])].offsets_for_role(roles.RED)
        and not caps[int(v.attrib["ID"])].offsets_for_role(roles.WHITE)
    )
    for value in list(findall_local(rest, "FixtureVal")):
        if value is not plain:
            rest.remove(value)
    plain_caps = caps[int(plain.attrib["ID"])]
    pairs = _pairs_of(plain)
    for role, level in zip((roles.RED, roles.GREEN, roles.BLUE), remainder, strict=True):
        for offset in plain_caps.offsets_for_role(role):
            pairs[offset] = level
    _write_pairs(plain, pairs)
    step_id = next_function_id(workspace.root)
    members = [int(emitters.attrib["ID"]), int(rest.attrib["ID"])]
    workspace.add_function(build_collection(step_id, "Pastel Partido", members))
    workspace.add_function(
        build_chaser(next_function_id(workspace.root), "Rueda Pastel", [step_id])
    )

    findings = [f for f in check_workspace(workspace, library) if f.rule_id == RULE_ID]
    assert [(f.message_id, f.function, f.fixtures) for f in findings] == [
        ("white_share_dropped_step", "Rueda Pastel", (plain_caps.fixture.name,))
    ]
    assert findings[0].fields["step"] == "Pastel Partido"


def test_2026_09_26_a_strobe_the_level_outbids(library):
    """2026-09-26, en-sala DMX audit (items 7 and 16): holding STROBO, STROBO
    SUAVE or any of the three flashes left both MiN Wash at 255 "Open". Their
    Dimmer/Strobe channel is in the Intensity group, merged HTP, and the level
    under every state holds it at 255: max(255, 236) is 255. Override only
    orders the faders; ForceLTP is what lets the lower strobe value through.
    Take ForceLTP back off the STROBO button and the rule must bite.
    """
    from qlctool.checks.rule_strobe_masked_by_htp import RULE_ID, check_strobe_masked_by_htp

    for name in SHOWS:
        workspace = _show(name)
        graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
        groups = group_fixtures(workspace.root)
        states = room_states(workspace.root, graph, groups)
        entries = {f: str(f) for f in states}
        assert check_strobe_masked_by_htp(graph, groups, workspace.root, states, entries) == []

    workspace = _show()
    strobe = _functions(workspace)["Strobo Rapido"].attrib["ID"]
    buttons = [
        b
        for b in iter_local(workspace.root, "Button")
        if find_local(b, "Function") is not None
        and find_local(b, "Function").get("ID") == strobe
        and (find_local(b, "Action").text or "") == "Flash"
    ]
    assert buttons, "no STROBO button"
    for button in buttons:
        action = find_local(button, "Action")
        assert action.get("ForceLTP") == "1"
        del action.attrib["ForceLTP"]

    findings = [f for f in check_workspace(workspace, library) if f.rule_id == RULE_ID]
    assert [f.function for f in findings] == ["Strobo Rapido"]
    assert findings[0].fixtures == ("MiN Wash #1", "MiN Wash #2")


def test_2026_09_26_a_forced_flash_that_cuts_the_smoke(library):
    """2026-09-26, ruling D1 of the en-sala fix plan: once the flashes force
    LTP so the MiN Wash strobe, every value they write wins, zeros included.
    `Flash 100%` wrote the smoke pumps 0, which would cut a smoke burst while
    FLASH is held - and the colour hits, forced since 2026-09-02, already did.
    A held flash neither starts nor stops smoke. Put the pump zeros back into
    `Flash 100%` and the rule must name the smoke machines.
    """
    from qlctool.checks.entry_points import entry_points
    from qlctool.checks.rule_flash_forced_zero import RULE_ID, check_flash_forced_zero

    for name, graph, groups in _shipped_graphs(library):
        root = _show(name).root
        assert check_flash_forced_zero(graph, groups, root, entry_points(root)) == [], name

    workspace = _show()
    scene = _functions(workspace)["Flash 100%"]
    caps = capabilities_of(workspace.root, library)
    smoke = {c.fixture.fixture_id: c for c in caps if c.is_smoke}
    written = {int(v.attrib["ID"]): v for v in findall_local(scene, "FixtureVal")}
    for fixture_id, capability in smoke.items():
        value = written.get(fixture_id)
        if value is None:
            tag = next(iter(written.values())).tag
            value = etree.SubElement(scene, tag, ID=str(fixture_id))
        pairs = _pairs_of(value)
        for offset in fog_offsets(capability):
            pairs[offset] = 0
        _write_pairs(value, pairs)

    findings = [f for f in check_workspace(workspace, library) if f.rule_id == RULE_ID]
    assert [f.function for f in findings] == ["Flash 100%"]
    assert set(findings[0].fixtures) == {c.fixture.name for c in smoke.values()}


def test_2026_09_26_a_bank_key_that_skips_the_front_pars(library):
    """2026-09-26, en-sala DMX audit (item 6): with the rig cyan, holding `1`
    turned it red - except the two CLB2.4 PARs and the four fog LED columns,
    which stayed cyan. Keys 1-0 hold one colour in every bank, and a bank is
    one fixture group's; those six are in no group. Ruling D9 puts them in the
    first bank's key scenes. Take the two PARs back out of the scene of `1`
    that holds them and the rule must name both - and so for the split of
    `9`, and for `1` bound to that one scene alone, as on a one-bank show:
    the rule judges which fixtures a key recolours, not how many colours or
    buttons it holds.
    """
    from qlctool.checks.rule_bank_key_coverage import RULE_ID, check_bank_key_coverage

    for name, graph, groups in _shipped_graphs(library):
        workspace = _show(name)
        states = room_states(workspace.root, graph, groups)
        assert check_bank_key_coverage(graph, groups, workspace.root, states) == [], name

    pars = {4, 5}
    expected = ("CLB2.4 Compact LED PAR System #1", "CLB2.4 Compact LED PAR System #2")
    for key in ("1", "9"):
        workspace = _show("Vibra.qxw")
        _drop_pars_from_key(workspace, key, pars)
        findings = [f for f in check_workspace(workspace, library) if f.rule_id == RULE_ID]
        assert [f.fields["trigger"] for f in findings] == [key]
        assert findings[0].fixtures == expected

    workspace = _show("Vibra.qxw")
    holder = _drop_pars_from_key(workspace, "1", pars)
    holder_id = holder.attrib["ID"]
    for button in iter_local(workspace.root, "Button"):
        function, key = find_local(button, "Function"), find_local(button, "Key")
        if key is not None and key.text == "1" and function.attrib.get("ID") != holder_id:
            button.remove(key)
    findings = [f for f in check_workspace(workspace, library) if f.rule_id == RULE_ID]
    assert [(f.fields["trigger"], f.fields["buttons"]) for f in findings] == [("1", 1)]
    assert set(expected) <= set(findings[0].fixtures)
