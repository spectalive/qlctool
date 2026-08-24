"""The self-running show: content, structure and a console with one AUTO button.

The shows are unattended, so what matters is that pressing one thing brings up
colour, movement, gobos and haze together - and that nothing in the build can
leave the smoke machine running.
"""

from pathlib import Path

import pytest

from qlctool.generate.canonical_show import KEYS, build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.patch_conflicts import patch_conflicts
from qlctool.fixture import patched_fixtures
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


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    ws = Workspace.load(SHOW)
    show = build_canonical_show(ws, FixtureLibrary.load())
    out = tmp_path_factory.mktemp("show") / "Vibra.qxw"
    ws.save(out)
    return show, out


def test_the_rig_survives_and_the_old_content_does_not(built):
    show, out = built
    root = Workspace.load(out).root

    assert len(patched_fixtures(root)) == 27
    assert patch_conflicts(root) == []
    assert len(_functions(root)) == show.function_count
    assert [b.group_name for b in show.banks] == ["BarrasLed", "Cabezas", "PAR"]


def test_auto_starts_everything_at_once(built):
    show, out = built
    functions = _functions(Workspace.load(out).root)

    auto = functions[str(show.master_ids["AUTO"])]
    assert auto.attrib["Type"] == "Collection"
    members = {step.text for step in findall_local(auto, "Step")}
    for name in ("Rueda Colores", "Movimientos Cabezas", "Gobo Animacion",
                 "Humo Auto"):
        assert str(show.master_ids[name]) in members
    # And the colour wheel is itself a collection of the per-group wheels.
    wheel = functions[str(show.master_ids["Rueda Colores"])]
    assert wheel.attrib["Type"] == "Collection"
    assert len(findall_local(wheel, "Step")) == len(show.banks)


def test_the_console_carries_the_old_keyboard_shortcuts(built):
    show, out = built
    root = Workspace.load(out).root
    buttons = {}
    for element in root.iter():
        if localname(element) != "Button":
            continue
        function = find_local(element, "Function")
        key = find_local(element, "Key")
        if function is not None and key is not None and key.text:
            buttons[int(function.attrib["ID"])] = (key.text, find_local(element, "Action").text)

    assert buttons[show.master_ids["AUTO"]] == ("Q", "Toggle")
    assert buttons[show.master_ids["Flash 100%"]] == ("Space", "Flash")
    assert buttons[show.master_ids["Todo Negro"]] == (KEYS["Todo Negro"], "Toggle")


def test_no_scene_but_the_smoke_ones_touches_the_smoke_machine(built):
    show, out = built
    root = Workspace.load(out).root
    functions = _functions(root)

    smoke_ids = {
        f.fixture_id for f in patched_fixtures(root) if "Smoke" in f.model
    }
    smoke_scene_names = {"Humo ON", "Humo OFF"}
    for function in functions.values():
        if function.attrib.get("Type") != "Scene":
            continue
        if function.attrib.get("Name") in smoke_scene_names:
            continue
        driven = {int(v.attrib["ID"]) for v in findall_local(function, "FixtureVal")}
        assert not (driven & smoke_ids), function.attrib.get("Name")


@pytest.mark.skipif(
    qlcplus_binary() is None, reason="QLC+ is not installed on this machine"
)
def test_qlcplus_loads_the_show(built):
    _, out = built
    result = validate_workspace(out)
    assert result.ok, result.describe()
