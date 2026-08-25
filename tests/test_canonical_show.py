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


def test_auto_is_a_colour_bed_a_haze_and_an_energy_cycle(built):
    """The colour and the haze run under everything; the level rides on top.

    Keeping the bed outside the cycle is what stops a level change from
    blacking the room out, and the effects that read as "peak" - fast movement,
    prism, the dimmer chase - are reachable only through the level that is one.
    """
    show, out = built
    functions = _functions(Workspace.load(out).root)

    auto = functions[str(show.master_ids["AUTO"])]
    assert auto.attrib["Type"] == "Collection"
    members = {step.text for step in findall_local(auto, "Step")}
    assert members == {
        str(show.master_ids[name])
        for name in ("Rueda Colores", "Humo Auto", "Ciclo Energia")
    }

    cycle = functions[str(show.master_ids["Ciclo Energia"])]
    assert cycle.attrib["Type"] == "Chaser"
    # A wave, not a ramp: it comes back down through the middle level.
    assert [functions[s.text].attrib["Name"] for s in findall_local(cycle, "Step")] == [
        "Nivel Ambiente", "Nivel Fiesta", "Nivel Peak", "Nivel Fiesta",
    ]

    party = functions[str(show.master_ids["Nivel Fiesta"])]
    party_members = {step.text for step in findall_local(party, "Step")}
    assert str(show.master_ids["Movimientos Cabezas"]) in party_members
    assert str(show.master_ids["Gobo Animacion"]) in party_members

    peak = functions[str(show.master_ids["Nivel Peak"])]
    peak_members = {step.text for step in findall_local(peak, "Step")}
    assert str(show.master_ids["Movimientos Rapidos"]) in peak_members
    assert str(show.master_ids["Dimmer Chase"]) in peak_members
    # Held back for the peak, not running all night.
    assert str(show.master_ids["Dimmer Chase"]) not in party_members
    # And the colour wheel is one wheel over the whole rig, not one per group:
    # three Random wheels never agree, and the heads and the PARs have to.
    wheel = functions[str(show.master_ids["Rueda Colores"])]
    assert wheel.attrib["Type"] == "Chaser"
    assert wheel.attrib["Name"] == "Rueda Colores"


def test_only_a_pixel_group_cycles_matrices_under_auto(built):
    """A matrix paints its own group's colour, so a cycle per group desyncs it.

    The bars and panels have cells to draw across and keep theirs; the heads
    and the PARs take their colour from the rig-wide wheel instead, which is
    the only way they land on white together.
    """
    show, out = built
    root = Workspace.load(out).root
    functions = _functions(root)

    # Reached through the energy levels now, which is where every effect that
    # is not the colour bed or the haze lives.
    running = set()
    for level in ("Nivel Ambiente", "Nivel Fiesta", "Nivel Peak"):
        collection = functions[str(show.master_ids[level])]
        running |= {step.text for step in findall_local(collection, "Step")}
    cycles = {
        functions[m].attrib["Name"]
        for m in running
        if functions[m].attrib["Name"].startswith("Ciclo Matrices")
    }
    assert cycles == {"Ciclo Matrices BarrasLed"}


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


def test_no_chaser_walks_itself_at_engine_speed(built):
    """Every chaser has to have a step duration QLC+ will actually wait on.

    ChaserRunner::stepDuration takes the step's time from the chaser when the
    duration mode is Common, and from the step itself in PerStep. Either way a
    duration of 0 is already over on the tick the step began, so the chaser
    walks a step per engine tick and the show flickers through itself.
    Common is preferred - a Speed Dial and Chaser::tap() only drive that mode -
    so PerStep is only for a chaser whose steps genuinely differ.
    """
    _, out = built

    for function in _functions(Workspace.load(out).root).values():
        if function.attrib.get("Type") != "Chaser":
            continue
        name = function.attrib.get("Name")
        holds = [int(s.attrib["Hold"]) for s in findall_local(function, "Step")]
        assert holds and all(h > 0 for h in holds), name

        mode = find_local(function, "SpeedModes").attrib["Duration"]
        if len(set(holds)) == 1:
            assert mode == "Common", name
            fade_in = int(find_local(function, "Speed").attrib["FadeIn"])
            duration = int(find_local(function, "Speed").attrib["Duration"])
            assert duration == fade_in + holds[0], name
        else:
            assert mode == "PerStep", name


def test_the_smoke_chaser_bursts_then_waits(built):
    """The burst and the wait are different lengths, so it has to be PerStep."""
    show, out = built
    smoke = _functions(Workspace.load(out).root)[str(show.master_ids["Humo Auto"])]

    assert find_local(smoke, "SpeedModes").attrib["Duration"] == "PerStep"
    holds = [int(s.attrib["Hold"]) for s in findall_local(smoke, "Step")]
    assert holds == [2000, 60000]
