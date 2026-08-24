"""Per-group colour banks: the shape the hand-built show actually uses."""

from pathlib import Path

import pytest

from qlctool.generate.color_banks import SPLIT_COLORS, generate_color_banks
from qlctool.library import FixtureLibrary
from qlctool.palette import PALETTE, PRIMARY_COLORS
from qlctool.validate import qlcplus_binary, validate_workspace
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, localname

REPO = Path(__file__).resolve().parents[3]
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
        # Ordered pairs of the split colours, both directions.
        assert len(bank.split_ids) == len(SPLIT_COLORS) * (len(SPLIT_COLORS) - 1)
        assert functions[str(bank.scene_ids[0])].attrib["Name"] == (
            f"{PRIMARY_COLORS[0]} {bank.group_name}"
        )
        wheel = functions[str(bank.wheel_id)]
        assert wheel.attrib["Type"] == "Chaser"
        # Random, because a fixed order reads as a loop when nobody is watching.
        assert find_local(wheel, "RunOrder").text == "Random"
        assert len(findall_local(wheel, "Step")) == len(bank.scene_ids)
        mix = functions[str(bank.mix_wheel_id)]
        assert len(findall_local(mix, "Step")) == len(bank.split_ids)


def test_a_split_alternates_two_colours_across_the_group(tmp_path):
    ws = Workspace.load(SHOW)
    banks = generate_color_banks(ws, FixtureLibrary.load())
    heads = next(b for b in banks if b.group_name == "Cabezas")

    functions = _functions(ws.root)
    split = next(
        f for f in (functions[str(i)] for i in heads.split_ids)
        if f.attrib["Name"] == "Rojo / Azul Cabezas"
    )
    values = findall_local(split, "FixtureVal")
    assert len(values) >= 4
    # First fixture red, second blue - that is what "Rojo / Azul" means.
    red, blue = PALETTE["Rojo"], PALETTE["Azul"]
    first = [int(v) for v in values[0].text.split(",")]
    second = [int(v) for v in values[1].text.split(",")]
    assert red[0] in first and blue[2] in second


@pytest.mark.skipif(
    qlcplus_binary() is None, reason="QLC+ is not installed on this machine"
)
def test_qlcplus_loads_the_banks(tmp_path):
    ws = Workspace.load(SHOW)
    generate_color_banks(ws, FixtureLibrary.load())
    out = tmp_path / "out.qxw"
    ws.save(out)

    assert validate_workspace(out).ok
