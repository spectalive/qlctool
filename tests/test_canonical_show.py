"""The self-running show: content, structure and a console with one AUTO button.

The shows are unattended, so what matters is that pressing one thing brings up
colour, movement, gobos and haze together - and that nothing in the build can
leave the smoke machine running.
"""

from pathlib import Path

import pytest

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.fixture_group import fixture_groups
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
    The pixel cycle is part of the bed too: the bars own their own colour, so
    whoever owns it has to keep owning it across a level change.
    """
    show, out = built
    functions = _functions(Workspace.load(out).root)

    auto = functions[str(show.master_ids["AUTO"])]
    assert auto.attrib["Type"] == "Collection"
    members = {step.text for step in findall_local(auto, "Step")}
    named = {
        str(show.master_ids[name])
        for name in ("Rueda Colores", "Humo Auto", "Ciclo Energia")
    }
    assert named <= members
    # Plus what the pixel groups need, which the wheel no longer gives them:
    # their own colour cycle, and the scene holding their intensity open.
    assert {functions[m].attrib["Name"] for m in members - named} == {
        "Ciclo Matrices BarrasLed", "Pixeles ON", "Ciclo Paneles",
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

    # Part of the bed, beside the colour wheel: a level that owns the bars'
    # colour hands it back on every step, and two levels running at once put
    # two colour sources on one fixture. The levels carry no colour at all now.
    auto = functions[str(show.master_ids["AUTO"])]
    cycles = {
        functions[m.text].attrib["Name"]
        for m in findall_local(auto, "Step")
        if functions[m.text].attrib["Name"].startswith("Ciclo Matrices")
    }
    assert cycles == {"Ciclo Matrices BarrasLed"}

    for level in ("Nivel Ambiente", "Nivel Fiesta", "Nivel Peak"):
        collection = functions[str(show.master_ids[level])]
        names = {
            functions[step.text].attrib["Name"]
            for step in findall_local(collection, "Step")
        }
        assert not any(n.startswith("Ciclo Matrices") for n in names), level


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


def test_one_fixture_never_has_two_colour_sources_under_auto(built):
    """RGB mixes HTP, so two sources on one fixture add up instead of choosing.

    A bar told red by the rig-wide wheel and blue by its own matrix came out
    magenta, and anything on top of that came out white. The pixel groups
    belong to their matrix; the wheel lights everything else.
    """
    _, out = built
    root = Workspace.load(out).root
    caps = {
        c.fixture.fixture_id: c
        for c in capabilities_of(root, FixtureLibrary.load())
    }
    painted = {
        fixture_id
        for group in fixture_groups(root)
        if group.name == "BarrasLed"
        for fixture_id in group.fixture_ids
    }
    assert painted, "no pixel group in this patch"

    for function in _functions(root).values():
        name = function.attrib.get("Name", "")
        if not name.startswith(("Rig ", "Cabezas ")):
            continue
        for value in findall_local(function, "FixtureVal"):
            fixture_id = int(value.attrib["ID"])
            if fixture_id not in painted or not value.text:
                continue
            numbers = [int(n) for n in value.text.split(",")]
            written = set(numbers[0::2])
            rgb = {
                offset
                for role in (roles.RED, roles.GREEN, roles.BLUE)
                for offset in caps[fixture_id].offsets_for_role(role)
            }
            assert not (written & rgb), (name, fixture_id)


def test_a_moment_brings_its_own_colour_bed(built):
    """A moment replaces AUTO, so whatever AUTO was providing has to come with
    it - otherwise pressing CHARLA leaves the room dark."""
    show, out = built
    functions = _functions(Workspace.load(out).root)

    for moment in (
        "Momento Charla", "Momento Tranquilo", "Momento Fiesta", "Momento Locura",
    ):
        collection = functions[str(show.master_ids[moment])]
        assert collection.attrib["Type"] == "Collection"
        members = {
            functions[step.text].attrib["Name"]
            for step in findall_local(collection, "Step")
        }
        lights_something = members & {
            "Rueda Colores", "Luz Charla", "Ciclo Matrices BarrasLed",
        }
        assert lights_something, (moment, members)

    # The speech look is the one with nothing moving in it.
    charla = functions[str(show.master_ids["Momento Charla"])]
    moving = {
        functions[step.text].attrib["Name"]
        for step in findall_local(charla, "Step")
    } & {"Rueda Colores", "Movimientos Cabezas", "Gobo Animacion",
         "Ciclo Matrices BarrasLed", "Dimmer Chase"}
    assert not moving, moving


def test_there_is_one_white_and_it_is_not_called_luces_on(built):
    """Three buttons drove full white on the same fixtures and no name said
    which was which."""
    show, _ = built
    assert "Blanco Total" in show.master_ids
    assert "Luces ON" not in show.master_ids
    assert "Todo Blanco" not in show.master_ids


def _pairs(function, fixture_id):
    """The (offset, value) a Scene writes to one fixture."""
    for value in findall_local(function, "FixtureVal"):
        if int(value.attrib["ID"]) != fixture_id or not value.text:
            continue
        numbers = [int(n) for n in value.text.split(",")]
        return dict(zip(numbers[0::2], numbers[1::2], strict=True))
    return {}


def test_everything_white_reaches_the_beams(built):
    """A beam has no RGB, so a colour scene skipped it and left it dark.

    Not dimmed and not the wrong colour: never written to. "Blanco Total" is
    the button somebody presses to see the room, and four 7R staying black is
    the most visible way for it to be wrong.
    """
    show, out = built
    root = Workspace.load(out).root
    caps = capabilities_of(root, FixtureLibrary.load())
    functions = _functions(root)

    wheel_only = [
        c for c in caps
        if c.has_role(roles.COLOR_MACRO)
        and not any(c.has_role(r) for r in (roles.RED, roles.GREEN, roles.BLUE))
    ]
    assert wheel_only, "no wheel-coloured fixture in this patch"

    for look, level in (("Blanco Total", 255), ("Flash 100%", 255),
                        ("Flash 50%", 128)):
        scene = functions[str(show.master_ids[look])]
        for capability in wheel_only:
            written = _pairs(scene, capability.fixture.fixture_id)
            assert written, (look, capability.fixture.name)
            for offset in capability.offsets_for_role(roles.DIMMER):
                assert written.get(offset) == level, (look, capability.fixture.name)
            wheel = capability.wheel_for_role(roles.COLOR_MACRO)
            assert wheel is not None and wheel[0] in written, look


def test_a_matrix_lit_fixture_has_its_intensity_opened(built):
    """A matrix writes RGB and nothing else.

    The panels keep a master dimmer on channel 1 and a shutter on channel 5,
    and no matrix touches either. The rig-wide wheel used to open them by
    accident; taking these fixtures off the wheel took that away too, and they
    went dark everywhere except under a flat scene like Flash 100%.
    """
    show, out = built
    root = Workspace.load(out).root
    caps = {
        c.fixture.fixture_id: c
        for c in capabilities_of(root, FixtureLibrary.load())
    }
    functions = _functions(root)

    base = functions[str(show.master_ids["Pixeles ON"])]
    assert base.attrib["Type"] == "Scene"

    painted = {
        fixture_id
        for group in fixture_groups(root)
        if group.name == "BarrasLed"
        for fixture_id in group.fixture_ids
    }
    needs_opening = [
        capability
        for fixture_id in painted
        if (capability := caps[fixture_id])
        and any(
            capability.has_role(role)
            for role in (roles.RED, roles.GREEN, roles.BLUE)
        )
        and capability.offsets_for_role(roles.DIMMER)
    ]
    assert needs_opening, "no matrix-lit fixture has a dimmer to open"
    for capability in needs_opening:
        written = _pairs(base, capability.fixture.fixture_id)
        for offset in capability.offsets_for_role(roles.DIMMER):
            assert written.get(offset) == 255, capability.fixture.name

    # It carries no colour: that is the matrix's, and two sources make white.
    for capability in needs_opening:
        written = _pairs(base, capability.fixture.fixture_id)
        for role in (roles.RED, roles.GREEN, roles.BLUE):
            for offset in capability.offsets_for_role(role):
                assert offset not in written, capability.fixture.name


def test_the_pixel_intensity_runs_wherever_the_pixel_cycle_does(built):
    """Colour without intensity is a fixture that is off. They travel together."""
    show, out = built
    functions = _functions(Workspace.load(out).root)
    base = str(show.master_ids["Pixeles ON"])

    for name in ("AUTO", "Momento Tranquilo", "Momento Fiesta", "Momento Locura"):
        collection = functions[str(show.master_ids[name])]
        members = {step.text for step in findall_local(collection, "Step")}
        cycles = {
            m for m in members
            if functions[m].attrib["Name"].startswith("Ciclo Matrices")
        }
        assert cycles, name
        assert base in members, name
