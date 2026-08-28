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
    The pixels' colour is part of the bed too: the wheel's own steps carry
    their matrices, so one clock owns the room's colour across a level change.
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
    # Plus what the pixel groups need beside the wheel, which carries their
    # colour inside its own steps: the scene holding their intensity open,
    # and the panels' phase cycle - their own programmes most of the night,
    # a stretch in manual listening to the wheel's RGB (2026-08-28).
    assert {functions[m].attrib["Name"] for m in members - named} == {
        "Pixeles ON", "Ciclo Paneles Mixto",
    }

    cycle = functions[str(show.master_ids["Ciclo Energia"])]
    assert cycle.attrib["Type"] == "Chaser"
    # A wave, not a ramp: the way down from the peak is the dynamic level,
    # party pace with the dimmers taking turns (2026-08-28).
    assert [functions[s.text].attrib["Name"] for s in findall_local(cycle, "Step")] == [
        "Nivel Ambiente", "Nivel Fiesta", "Nivel Peak", "Nivel Fiesta Dinamico",
    ]

    def _names(level):
        collection = functions[str(show.master_ids[level])]
        return {
            functions[step.text].attrib["Name"]
            for step in findall_local(collection, "Step")
        }

    # 2026-08-27, the owner on pressing AUTO and watching parked heads: "el
    # auto es eso, como el modo auto de las cabezas en si". Every level moves
    # from the first second - the quiet one slowly, on the washes, with the
    # beams fanned - and every level owns its intensity, low or full.
    ambient = _names("Nivel Ambiente")
    assert "Movimientos Suaves" in ambient
    assert "Beams Abanico" in ambient
    assert "Intensidad Ambiente" in ambient

    party = _names("Nivel Fiesta")
    assert {"Movimientos Washes", "Movimientos Beams",
            "Gobo Animacion", "Intensidad Total"} <= party

    # 2026-08-27: Peak is the one level `Dimmer Chase` actually owns. Before
    # this, `Intensidad Total` ran beside it here too and held every dimmer at
    # 255 - HTP means the chase's dips could never win, so it was cosmetic
    # (TODO.md). `Intensidad Peak` is its replacement: a static owner only for
    # the fixtures the chase cannot reach at all (no dimmer role).
    peak = _names("Nivel Peak")
    assert {"Rapidos Washes", "Rapidos Beams", "Dimmer Chase",
            "Intensidad Peak"} <= peak
    assert "Intensidad Total" not in peak
    # Held back for the peak, not running all night.
    assert "Dimmer Chase" not in party
    # And the colour wheel is one wheel over the whole rig, not one per group:
    # three Random wheels never agree, and the heads and the PARs have to.
    wheel = functions[str(show.master_ids["Rueda Colores"])]
    assert wheel.attrib["Type"] == "Chaser"
    assert wheel.attrib["Name"] == "Rueda Colores"


def test_dimmer_chase_owns_peak_and_nothing_is_left_dark(built):
    """2026-08-27: `Dimmer Chase` in Peak was cosmetically dead.

    `intensidad tapada` cannot see this shape at all: it only counts Scene and
    Sequence writes (`rule_shadowed_intensity._dimmer_writes`), on purpose - an
    EFX's actual output is not one knowable value, so the rule treats it as "we
    don't know" rather than risk a false alarm. Sharpening it to count a
    Dimmer-mode EFX as a writer would also light up `Momento Locura`, which
    pairs the very same chase with `Intensidad Total` on purpose and stays that
    way (out of scope here) - a real false positive on a shipped workspace, not
    a missed catch. So the proof lives here instead, at the generator level:
    reproduce the old shape and show analytically that a static 255 - the DMX
    ceiling - shadows every channel the chase could ever write to, then confirm
    the generated Peak no longer pairs them, and that the fixtures the chase
    cannot dim (the MiN Wash - no dimmer role, its light lives behind a shutter
    range) still have an owner so they are not left dark. The full check gate
    over the real shipped shows is `test_check.py`'s.
    """
    from qlctool.checks.driven_channels import driven_channels

    show, out = built
    root = Workspace.load(out).root
    functions = _functions(root)
    library = FixtureLibrary.load()
    caps = {c.fixture.fixture_id: c for c in capabilities_of(root, library)}

    # 2026-08-28: the chase went back to the hand-built shape - a Collection
    # of per-family Serial Line cascades - so its writes are the union of its
    # members' (driven_channels returns {} for the Collection itself).
    chase = functions[str(show.master_ids["Dimmer Chase"])]
    chase_writes: dict[int, dict[int, int | None]] = {}
    chase_parts = (
        [functions[step.text] for step in findall_local(chase, "Step")]
        if chase.attrib["Type"] == "Collection" else [chase]
    )
    for part in chase_parts:
        for fixture_id, pairs in driven_channels(part, caps, {}).items():
            chase_writes.setdefault(fixture_id, {}).update(pairs)
    assert chase_writes, "the chase should drive at least one fixture's dimmer"

    total = functions[str(show.master_ids["Intensidad Total"])]
    total_writes = driven_channels(total, caps, {})
    # RED, reproduced: for every fixture `Intensidad Total` actually reaches
    # (it deliberately skips the pixel groups and the panels - a separate
    # owner each, unrelated to this bug), the channel the chase drives was
    # also a 255 there - HTP can never show anything but that ceiling.
    shadowed = 0
    for fixture_id, offsets in chase_writes.items():
        if fixture_id not in total_writes:
            continue
        for offset in offsets:
            assert total_writes[fixture_id].get(offset) == 255, (
                "the old bug should still shadow every channel the chase owns"
            )
            shadowed += 1
    assert shadowed, "the chase and `Intensidad Total` should overlap somewhere"

    # GREEN: Peak itself does not carry `Intensidad Total` any more, and
    # nothing else in Peak contests the chase's own channels.
    peak = functions[str(show.master_ids["Nivel Peak"])]
    peak_members = {step.text for step in findall_local(peak, "Step")}
    assert str(show.master_ids["Intensidad Total"]) not in peak_members

    chase_step_id = str(show.master_ids["Dimmer Chase"])
    other_writes: dict[int, dict[int, int | None]] = {}
    for member_id in peak_members - {chase_step_id}:
        for fixture_id, pairs in driven_channels(
            functions[member_id], caps, {}
        ).items():
            other_writes.setdefault(fixture_id, {}).update(pairs)
    for fixture_id, offsets in chase_writes.items():
        contested = set(offsets) & set(other_writes.get(fixture_id, {}))
        assert not contested, "something besides the chase owns its dimmers"

    # Nothing goes dark: the fixture the chase cannot dim at all (no dimmer
    # role - found by capability, not by name) still has an owner in Peak.
    static_id = show.master_ids.get("Intensidad Peak")
    assert static_id is not None, "Peak needs an owner for fixtures the chase skips"
    static_writes = driven_channels(functions[str(static_id)], caps, {})
    assert static_writes, "the static owner should light at least one fixture"
    # The static owner never bids on a dimmer the chase owns - HTP, the chase's
    # dips could never win. What it does write on the dimmered fixtures is
    # their strobe-off (2026-08-28): a flash released during a chase level
    # used to latch the strobe until the next level's intensity base cleared
    # it, because nothing in the level wrote the channel back.
    for fixture_id, written in static_writes.items():
        dimmers = set(caps[fixture_id].offsets_for_role(roles.DIMMER))
        assert not (dimmers & set(written)), (
            "the static owner must not contest the chase's dimmers"
        )
    min_wash_ids = {
        c.fixture.fixture_id for c in caps.values() if c.fixture.model == "MiN Wash"
    }
    assert min_wash_ids and min_wash_ids <= static_writes.keys()


def test_only_a_pixel_group_gets_matrices_inside_the_wheel(built):
    """Two chasers that each rotate colour never agree, so there is one clock.

    The bars' colour rides inside the rig-wide wheel: each of its steps starts
    a matrix of the step's own colour over the group that has pixels to draw
    on, and nothing else in AUTO rotates colour - the standalone matrix cycle
    stays on the console for a person, and out of the room states.
    """
    show, out = built
    root = Workspace.load(out).root
    functions = _functions(root)

    auto = functions[str(show.master_ids["AUTO"])]
    names = {functions[m.text].attrib["Name"] for m in findall_local(auto, "Step")}
    assert not any(n.startswith("Ciclo Matrices") for n in names)

    wheel = functions[str(show.master_ids["Rueda Colores"])]
    steps = [functions[s.text] for s in findall_local(wheel, "Step")]
    assert steps and all(s.attrib["Type"] == "Collection" for s in steps)
    matrices = [
        functions[member.text]
        for step in steps
        for member in findall_local(step, "Step")
        if functions[member.text].attrib["Type"] == "RGBMatrix"
    ]
    assert len(matrices) == len(steps), "every wheel step colours the pixels"
    pixel_group = next(
        str(g.group_id) for g in fixture_groups(root) if g.name == "BarrasLed"
    )
    assert {find_local(m, "FixtureGroup").text for m in matrices} == {pixel_group}
    # The step's scene and its matrix state the same colour, by name: the
    # solid steps their own, a contrast step the colour of the "resto". The
    # multicolour steps are the exception that proves the clock: no single
    # colour to agree on, so their matrix is the rainbow plasma (2026-08-28) -
    # and the recovered "Rig 4 Colores" deals (same audit) are multicolour
    # steps by nature, so they ride the same plasma.
    for step, matrix in zip(steps, matrices, strict=True):
        if step.attrib["Name"].startswith(("Rig Multicolor", "Rig 4 Colores")):
            assert "Plasma Rainbow (Rueda)" in matrix.attrib["Name"]
            continue
        colour = step.attrib["Name"].split(" + ")[0].split()[-1]
        assert f" {colour} (Rueda)" in matrix.attrib["Name"], step.attrib["Name"]

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


def test_no_scene_but_the_smoke_ones_touches_the_smoke_pump(built):
    """The pump, not the fixture: a lit fog machine's LED joins the colour bed
    like a floor PAR, so ordinary scenes may write it - but a value above zero
    on any pump channel outside the smoke scenes is a tank emptying itself."""
    from qlctool.fog_offsets import fog_offsets

    show, out = built
    root = Workspace.load(out).root
    functions = _functions(root)

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
        for value in findall_local(function, "FixtureVal"):
            fixture_id = int(value.attrib["ID"])
            if fixture_id not in pumps or not value.text:
                continue
            numbers = [int(n) for n in value.text.split(",")]
            fired = [
                (offset, level)
                for offset, level in zip(numbers[0::2], numbers[1::2])
                if offset in pumps[fixture_id] and level > 0
            ]
            assert not fired, (function.attrib.get("Name"), fired)


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

    # Both flashes at full: "50%" is half the strobe *speed*, not half the
    # brightness - what it meant on the hand-built console (2026-08-27).
    for look, level in (("Blanco Total", 255), ("Flash 100%", 255),
                        ("Flash 50%", 255)):
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


def test_the_pixel_intensity_runs_wherever_the_wheel_does(built):
    """Colour without intensity is a fixture that is off. They travel together.

    The wheel's steps paint the pixel groups through their matrices, and a
    matrix writes RGB and nothing else - so every state that starts the wheel
    starts the scene holding their dimmers and shutters open beside it.
    """
    show, out = built
    functions = _functions(Workspace.load(out).root)
    base = str(show.master_ids["Pixeles ON"])
    wheel = str(show.master_ids["Rueda Colores"])

    for name in ("AUTO", "Momento Tranquilo", "Momento Fiesta", "Momento Locura"):
        collection = functions[str(show.master_ids[name])]
        members = {step.text for step in findall_local(collection, "Step")}
        assert wheel in members, name
        assert base in members, name
