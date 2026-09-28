"""The canonical show's timing: the smoke, the chasers' step lengths and the BPM tap.

Split by topic out of the original `test_canonical_show.py` (over the
codeality test-file line cap).
"""

import pytest
from rig_root import RIG_ROOT

from qlctool.capabilities_of import capabilities_of
from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.fog_offsets import fog_offsets
from qlctool.generate.build_canonical_show import build_canonical_show
from qlctool.localname import localname
from qlctool.qlcplus_binary import qlcplus_binary
from qlctool.validate_workspace import validate_workspace
from qlctool.workspace import Workspace

REPO = RIG_ROOT
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


def test_no_scene_but_the_smoke_ones_touches_the_smoke_pump(built):
    """The pump, not the fixture: a lit fog machine's LED joins the colour bed
    like a floor PAR, so ordinary scenes may write it - but a value above zero
    on any pump channel outside the smoke scenes is a tank emptying itself."""

    from qlctool.checks.build_show_graph import build_show_graph
    from qlctool.checks.valid_desk_bursts import valid_desk_bursts

    _show, out = built
    root = Workspace.load(out).root
    functions = _functions(root)
    graph = build_show_graph(root, capabilities_of(root, FixtureLibrary.load()))
    # 2026-09-13: only structurally verified private copies qualify as bursts.
    private_scenes = {
        scene_id for burst in valid_desk_bursts(graph, root) for scene_id in graph.members[burst]
    }

    pumps = {
        c.fixture.fixture_id: set(fog_offsets(c))
        for c in capabilities_of(root, FixtureLibrary.load())
        if c.is_smoke
    }
    smoke_scene_names = {"Humo ON", "Humo OFF", "Humo Vertical YA"}
    for function in functions.values():
        if function.attrib.get("Type") != "Scene":
            continue
        if function.attrib.get("Name") in smoke_scene_names:
            continue
        if int(function.attrib["ID"]) in private_scenes:
            continue
        for value in findall_local(function, "FixtureVal"):
            fixture_id = int(value.attrib["ID"])
            if fixture_id not in pumps or not value.text:
                continue
            numbers = [int(n) for n in value.text.split(",")]
            fired = [
                (offset, level)
                for offset, level in zip(numbers[0::2], numbers[1::2], strict=True)
                if offset in pumps[fixture_id] and level > 0
            ]
            assert not fired, (function.attrib.get("Name"), fired)


@pytest.mark.skipif(qlcplus_binary() is None, reason="QLC+ is not installed on this machine")
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
    so PerStep is for differing steps or a verified desk burst with a fixed clock.
    """
    _, out = built
    from qlctool.checks.build_show_graph import build_show_graph
    from qlctool.checks.valid_desk_bursts import valid_desk_bursts

    root = Workspace.load(out).root
    bursts = valid_desk_bursts(build_show_graph(root, []), root)
    for function in _functions(root).values():
        if function.attrib.get("Type") != "Chaser":
            continue
        name = function.attrib.get("Name")
        holds = [int(s.attrib["Hold"]) for s in findall_local(function, "Step")]
        assert holds and all(h > 0 for h in holds), name

        mode = find_local(function, "SpeedModes").attrib["Duration"]
        if int(function.attrib["ID"]) in bursts:
            assert mode == "PerStep", name
        elif len(set(holds)) == 1:
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


def test_tranquilo_rests_the_heads_instead_of_parking_them(built):
    """2026-08-29: Tranquilo held the heads parked dead at home, and a parked
    mover in a lull reads as a broken one ("molaría un movimiento suave
    estilo reposo", owner). The lull now breathes: each family on its own slow
    shapes, and home stays out of the moment. The beams rested in their fan
    here until the owner watched AUTO the same day and reported the 7R not
    moving - a static scene is a rest for a step, not for a whole lull.
    """
    show, out = built
    root = Workspace.load(out).root
    functions = _functions(root)

    tranquilo = functions[str(show.master_ids["Momento Tranquilo"])]
    members = {step.text for step in findall_local(tranquilo, "Step")}
    names = {functions[m].attrib.get("Name") for m in members}

    assert "Movimientos Suaves" in names
    assert "Suaves Washes" not in names
    assert "Suaves Beams" not in names
    assert "Beams Abanico" not in names
    assert str(show.master_ids["Cabezas Centro"]) not in members


def test_the_build_for_a_newer_qlcplus_taps_the_global_bpm(tmp_path):
    """Ready for the QLC+ that has ControlBPM - 5.2.2 does not.

    5.2.2 logs "Unknown speed dial tag: ControlBPM" and ignores the element,
    which is why this is `newshow --bpm-tap` and not the default. There the
    tap sets one global BPM and every layer counts its own beats against it,
    so nothing needs a multiplier at all.
    """
    ws = Workspace.load(SHOW)
    build_canonical_show(ws, FixtureLibrary.load(), bpm_tap=True)
    out = tmp_path / "future.qxw"
    ws.save(out)
    root = Workspace.load(out).root

    dial = next(d for d in root.iter() if localname(d) == "SpeedDial")
    assert dial.attrib["Caption"] == "Tempo Show"
    assert find_local(dial, "ControlBPM").text == "True"
    assert findall_local(dial, "Function") == []

    generator = find_local(
        find_local(find_local(root, "Engine"), "InputOutputMap"), "BeatGenerator"
    )
    assert generator.attrib["BeatType"] == "Internal"
    assert generator.attrib["BPM"] == "120"

    beats = [
        f
        for f in _functions(root).values()
        if (tempo := find_local(f, "Tempo")) is not None and tempo.text == "Beats"
    ]
    assert beats, "nothing counts beats for the BPM to move"
    # Never an EFX-stepping chaser: it hands its fade to the EFX as a raw
    # number and the figure collapses (2026-08-29, the 6 s head sweep).
    by_id = _functions(root)
    for chaser in beats:
        kinds = {
            by_id[s.text].attrib["Type"] for s in findall_local(chaser, "Step") if s.text in by_id
        }
        assert "EFX" not in kinds, chaser.attrib["Name"]
