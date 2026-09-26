"""Per-group colour banks: the shape the hand-built show actually uses."""

import pytest
from rig_root import RIG_ROOT

from qlctool.generate.generate_color_banks import generate_color_banks
from qlctool.key_split_pairs import KEY_SPLIT_PAIRS
from qlctool.library import FixtureLibrary
from qlctool.palette import PALETTE, PRIMARY_COLORS
from qlctool.split_pairs import SPLIT_PAIRS
from qlctool.validate import qlcplus_binary, validate_workspace
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, localname

REPO = RIG_ROOT
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"


def _functions(root):
    return {
        f.attrib["ID"]: f
        for f in find_local(root, "Engine")
        if localname(f) == "Function" and f.attrib.get("ID")
    }


def test_every_group_gets_a_bank_and_two_wheels(tmp_path):
    ws = Workspace.load(SHOW)

    banks = generate_color_banks(ws, FixtureLibrary.load())

    assert [b.group_name for b in banks] == ["BarrasLed", "Cabezas", "PAR"]
    out = tmp_path / "out.qxw"
    ws.save(out)
    functions = _functions(Workspace.load(out).root)

    for bank in banks:
        assert len(bank.scene_ids) == len(PRIMARY_COLORS)
        # The neighbouring pairs both ways round, plus the show's own keys.
        assert len(bank.split_ids) == len(SPLIT_PAIRS)
        assert functions[str(bank.scene_ids[0])].attrib["Name"] == (
            f"{PRIMARY_COLORS[0]} {bank.group_name}"
        )
        wheel = functions[str(bank.wheel_id)]
        assert wheel.attrib["Type"] == "Chaser"
        # Random, because a fixed order reads as a loop when nobody is watching.
        assert find_local(wheel, "RunOrder").text == "Random"
        # Every solid but white: white stays a hand pick (key 8) and no
        # rotation steps it ("luz blanca solo para blanco total", 2026-09-22).
        stepped = {functions[s.text].attrib["Name"] for s in findall_local(wheel, "Step")}
        assert stepped == {
            functions[str(i)].attrib["Name"]
            for i in bank.scene_ids
            if not functions[str(i)].attrib["Name"].startswith("Blanco")
        }
        mix = functions[str(bank.mix_wheel_id)]
        assert len(findall_local(mix, "Step")) == len(bank.split_ids)


def test_a_split_alternates_two_colours_across_the_group(tmp_path):
    ws = Workspace.load(SHOW)
    banks = generate_color_banks(ws, FixtureLibrary.load())
    heads = next(b for b in banks if b.group_name == "Cabezas")

    functions = _functions(ws.root)
    split = next(
        f
        for f in (functions[str(i)] for i in heads.split_ids)
        if f.attrib["Name"] == "Rojo / Azul Cabezas"
    )
    values = findall_local(split, "FixtureVal")
    assert len(values) >= 4
    # First fixture red, second blue - that is what "Rojo / Azul" means.
    red, blue = PALETTE["Rojo"], PALETTE["Azul"]
    first = [int(v) for v in values[0].text.split(",")]
    second = [int(v) for v in values[1].text.split(",")]
    assert red[0] in first and blue[2] in second


@pytest.mark.skipif(qlcplus_binary() is None, reason="QLC+ is not installed on this machine")
def test_qlcplus_loads_the_banks(tmp_path):
    ws = Workspace.load(SHOW)
    generate_color_banks(ws, FixtureLibrary.load())
    out = tmp_path / "out.qxw"
    ws.save(out)

    assert validate_workspace(out).ok


def _fixtures_of(function):
    return {int(v.attrib["ID"]) for v in findall_local(function, "FixtureVal")}


def test_the_ungrouped_fixtures_join_only_the_first_banks_key_scenes():
    """2026-09-26, en-sala DMX audit (ruling D9): the two CLB2.4 PARs are in
    no group, so they join the scenes the first bank's keys press - the first
    eight solids and the two key splits - and nothing else of it.
    """
    ws = Workspace.load(SHOW)
    extras = {4, 5}

    first, *rest = generate_color_banks(ws, FixtureLibrary.load())

    functions = _functions(ws.root)
    carrying = {
        i for i in first.scene_ids + first.split_ids if extras <= _fixtures_of(functions[str(i)])
    }
    assert carrying == set(first.key_ids)
    for bank in rest:
        for i in bank.scene_ids + bank.split_ids:
            assert not extras & _fixtures_of(functions[str(i)])


def test_a_one_fixture_first_bank_builds_no_split_on_the_extras():
    """2026-09-26, en-sala DMX audit (ruling D9): a split needs two of the
    group's own fixtures; the ungrouped ones added to a key split do not make
    a lone fixture into one. Such a bank keeps plain solids on every key.
    Only the key splits are asked for, so the guard meets a keyed split first.
    """
    ws = Workspace.load(SHOW)
    group = next(g for g in findall_local(find_local(ws.root, "Engine"), "FixtureGroup"))
    for head in findall_local(group, "Head")[1:]:
        group.remove(head)

    first = generate_color_banks(ws, FixtureLibrary.load(), split_pairs=KEY_SPLIT_PAIRS)[0]

    assert first.split_ids == []
    assert first.key_ids == first.scene_ids
    functions = _functions(ws.root)
    for i in first.scene_ids:
        assert {4, 5} <= _fixtures_of(functions[str(i)])
