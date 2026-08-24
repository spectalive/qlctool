"""The channel walk that settles what an undocumented fixture's channels do."""

from pathlib import Path

import pytest

from qlctool.generate.channel_probe import generate_channel_probe
from qlctool.validate import qlcplus_binary, validate_workspace
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, iter_local

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"
HYULIGHTS = 25  # 8 channels, one of the fixtures with no usable manual


def test_probe_walks_every_channel_once(tmp_path):
    ws = Workspace.load(SHOW)

    result = generate_channel_probe(ws, HYULIGHTS)

    assert len(result.scene_ids) == 8
    out = tmp_path / "out.qxw"
    ws.save(out)
    reloaded = Workspace.load(out).root

    scenes = {
        f.attrib["Name"]: f
        for f in iter_local(reloaded, "Function")
        if f.attrib.get("ID") in {str(i) for i in result.scene_ids}
    }
    assert len(scenes) == 8
    for offset in range(8):
        name = next(n for n in scenes if n.endswith(f"CH{offset + 1:02d} = 255"))
        values = findall_local(scenes[name], "FixtureVal")
        assert len(values) == 1
        assert values[0].attrib["ID"] == str(HYULIGHTS)
        assert values[0].text == f"{offset},255"

    chaser = next(
        f for f in iter_local(reloaded, "Function")
        if f.attrib.get("ID") == str(result.chaser_id)
    )
    # SingleShot: it walks the channels once and stops, rather than looping.
    assert find_local(chaser, "RunOrder").text == "SingleShot"


def test_base_values_hold_other_channels_open():
    ws = Workspace.load(SHOW)
    result = generate_channel_probe(ws, HYULIGHTS, base_values={0: 255})

    first = next(
        f for f in iter_local(ws.root, "Function")
        if f.attrib.get("ID") == str(result.scene_ids[1])
    )
    # Channel 2 under test, channel 1 (the dimmer) held open.
    assert findall_local(first, "FixtureVal")[0].text == "0,255,1,255"

    # The scene probing the base channel itself does not write it twice.
    probing_base = next(
        f for f in iter_local(ws.root, "Function")
        if f.attrib.get("ID") == str(result.scene_ids[0])
    )
    assert findall_local(probing_base, "FixtureVal")[0].text == "0,255"


def test_probe_rejects_an_unpatched_fixture():
    ws = Workspace.load(SHOW)
    with pytest.raises(KeyError, match="no patched fixture with ID 999"):
        generate_channel_probe(ws, 999)


@pytest.mark.skipif(
    qlcplus_binary() is None, reason="QLC+ is not installed on this machine"
)
def test_qlcplus_loads_a_probe(tmp_path):
    ws = Workspace.load(SHOW)
    generate_channel_probe(ws, HYULIGHTS)
    out = tmp_path / "out.qxw"
    ws.save(out)

    assert validate_workspace(out).ok
