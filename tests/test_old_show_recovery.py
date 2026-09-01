"""What the hand-built show had right and the generator lost - pinned.

Every test here is dated 2026-08-28 and comes from the old-vs-new audit
(`docs/old-vs-new-audit-2026-08-28.md`): a semantic comparison of
DeluxeEventos2.qxw against the three generated Vibra workspaces found six
likely-forgotten behaviors and a handful of judgement calls the owner asked to
have back ("recupera todo lo que tanto me costó"). These tests put each one
back into a generated show and bite if the generator loses it again.
"""

from pathlib import Path

import pytest

from qlctool.generate.canonical_show import KEYS, build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.palette import PALETTE
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, iter_local, localname

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


def test_every_palette_colour_reaches_the_show(built):
    """Audit finding 2: seven of the eighteen palette colours existed only as
    Python constants - Rojo Fuego, Verde Menta, Celeste, Azul Cielo, Azul
    Profundo, Morado and Fucsia never reached any Scene or RGBMatrix. The
    palette's whole point is that a generated show looks like the hand-built
    one; a colour nothing emits is a lie in the module docstring."""
    _, out = built
    root = Workspace.load(out).root

    emitted: set[tuple[int, int, int]] = set()
    for function in _functions(root).values():
        if function.attrib["Type"] == "RGBMatrix":
            for tag in ("MonoColor", "EndColor"):
                element = find_local(function, tag)
                if element is not None and element.text:
                    argb = int(element.text)
                    emitted.add(((argb >> 16) & 255, (argb >> 8) & 255, argb & 255))
    missing = {name for name, rgb in PALETTE.items() if rgb not in emitted}
    # Scenes emit the primary colours; the matrices must cover the rest. The
    # assertion is over matrices alone because that is where the seven lost
    # colours were put back - if this fails, run the audit again.
    assert not missing, f"palette colours no generated function emits: {missing}"


def test_keys_nine_and_zero_are_the_blue_red_splits(built):
    """Audit finding 3: on every old colour bank, key 9 was the alternating
    blue/red look and key 0 red/blue; the generator had put Naranja and Rosa
    there. Muscle memory is the reason the banks keep keys at all."""
    show, out = built
    root = Workspace.load(out).root
    functions = _functions(root)

    for bank in show.banks:
        keyed = bank.key_ids
        assert len(keyed) == 10, bank.group_name
        ninth = functions[str(keyed[8])].attrib["Name"]
        tenth = functions[str(keyed[9])].attrib["Name"]
        assert ninth.startswith("Azul / Rojo "), (bank.group_name, ninth)
        assert tenth.startswith("Rojo / Azul "), (bank.group_name, tenth)


def test_the_rainbows_are_back_and_relative(built):
    """Audit finding 5: `Arcoiris Simultáneo` and `Arcoiris Pasos` - relative
    Circle EFX in RGB mode over the whole rig, on their own keys - had no
    equivalent among 32 absolute pan/tilt EFX."""
    show, out = built
    root = Workspace.load(out).root
    functions = _functions(root)

    for name, spread in (("Arcoiris Simultaneo", False), ("Arcoiris Pasos", True)):
        efx = functions[str(show.master_ids[name])]
        assert efx.attrib["Type"] == "EFX"
        assert find_local(efx, "IsRelative").text == "1"
        assert find_local(efx, "Algorithm").text == "Circle"
        fixtures = findall_local(efx, "Fixture")
        assert len(fixtures) > 10  # the whole RGB rig, per head
        assert all(find_local(f, "Mode").text == "2" for f in fixtures)
        offsets = {find_local(f, "StartOffset").text for f in fixtures}
        assert (len(offsets) > 1) == spread, name
    assert KEYS["Arcoiris Simultaneo"] == "'"
    assert KEYS["Arcoiris Pasos"] == "¡"


def test_the_panel_speed_ride_is_back(built):
    """Audit finding 6: `Strobo LED - Random SPEED` glided the panels' speed
    channel 160-232-200-255 with 45 s fades and a minute per value; the
    generated show kept only the manual fader."""
    show, out = built
    root = Workspace.load(out).root
    functions = _functions(root)

    chaser = functions[str(show.master_ids["Vel. Paneles Auto"])]
    assert chaser.attrib["Type"] == "Chaser"
    steps = findall_local(chaser, "Step")
    values = []
    for step in steps:
        scene = functions[step.text]
        for fixture_val in findall_local(scene, "FixtureVal"):
            pairs = fixture_val.text.split(",")
            values.append(int(pairs[1]))
            break  # every panel gets the same value; one is the claim
    assert values == [160, 232, 200, 255]
    speed = find_local(chaser, "Speed")
    assert speed.attrib["FadeIn"] == "45000"


def test_the_beams_park_at_the_old_rest(built):
    """Audit finding 4: `Cabezas Reposo` laid the four 7R beams at pan 0,
    tilt 130, aimed on the real rig; `Cabezas Centro` had normalised them to
    (127,127), which is a different look, not a different name for it."""
    show, out = built
    root = Workspace.load(out).root
    functions = _functions(root)

    centro = functions[str(show.master_ids["Cabezas Centro"])]
    beam_rows = [
        fixture_val
        for fixture_val in findall_local(centro, "FixtureVal")
        if int(fixture_val.attrib["ID"]) in (20, 21, 22, 23)  # the 7R beams
    ]
    assert len(beam_rows) == 4
    for fixture_val in beam_rows:
        pairs = dict(zip(*[iter(map(int, fixture_val.text.split(",")))] * 2))
        # 7R 16 channel: pan on offset 0, tilt on offset 1.
        assert pairs[0] == 0 and pairs[1] == 130, fixture_val.attrib["ID"]


def test_the_prism_animation_is_the_old_choreography(built):
    """Audit finding (judgement call, restored): the old `Prisma Animacion`
    was eight ordered steps - single beams and mirrored pairs taking the
    prism in turn, all-in as the crest, all-out as the rest - not a two-step
    toggle."""
    show, out = built
    root = Workspace.load(out).root
    functions = _functions(root)

    chaser = functions[str(show.master_ids["Prisma Animacion"])]
    names = [functions[s.text].attrib["Name"] for s in findall_local(chaser, "Step")]
    # The dance is the first eight steps and stays that way. Since 2026-08-30
    # the same prism keeps turning after it at the other two speeds the
    # rotation channel can do - extra steps, never a reordering.
    assert names[8:] == ["Prisma Giro Rapido", "Prisma Giro Inverso"]
    assert names[:8] == [
        "Prisma - 4",
        "Prisma - 2 y 4",
        "Prisma - 1",
        "Prisma - 2",
        names[4],
        "Prisma - 3",
        "Prisma - 1 y 3",
        names[7],
    ]
    # Crest and rest are the wheel's own scenes: inserted, then parked.
    assert names[4] != names[7]
    assert find_local(chaser, "RunOrder").text == "Loop"


def test_the_matrix_cycles_are_random_like_the_old_one(built):
    """Audit finding (judgement call, restored): the old 121-step bar cycle
    ran Random; the generated cycles ran Loop against the show's own rule
    that everything cycling is Random."""
    _, out = built
    root = Workspace.load(out).root

    cycles = [
        f
        for f in _functions(root).values()
        if f.attrib.get("Name", "").startswith("Ciclo Matrices")
    ]
    assert cycles
    for cycle in cycles:
        assert find_local(cycle, "RunOrder").text == "Random", cycle.attrib["Name"]


def test_the_output_binds_to_whatever_interface_is_connected(built):
    """Audit finding 1: the shipped files carried two different FT232R serial
    numbers; a workspace opened with the other interface attached outputs
    nothing. docs/rig.md: the binding is generic (`UID="None"`)."""
    _, out = built
    root = Workspace.load(out).root

    outputs = list(iter_local(root, "Output"))
    assert outputs
    for output in outputs:
        assert output.attrib["Plugin"] == "DMX USB"
        assert output.attrib["UID"] == "None"
        assert "Name" not in output.attrib


def test_the_quad_colour_deals_ride_the_wheel(built):
    """Audit finding (judgement call, restored): the four deterministic
    "4 Colores" rotations - blue/red/green/white dealt across the rig, the
    deal walking one seat per scene - are wheel steps beside the wild
    multicolor ones."""
    show, out = built
    root = Workspace.load(out).root
    functions = _functions(root)

    wheel = functions[str(show.master_ids["Rueda Colores"])]
    step_names = [functions[s.text].attrib["Name"] for s in findall_local(wheel, "Step")]
    quads = [n for n in step_names if n.startswith("Rig 4 Colores")]
    assert len(quads) == 4


def test_movement_keeps_the_simultaneo_twins_and_the_crossfade(built):
    """Audit finding (judgement call, restored): every shape had a
    "(Simultaneo)" twin - all heads at the same phase - and the movement
    rotation crossfaded 5 s between blocks (old Chaser 23)."""
    show, out = built
    root = Workspace.load(out).root
    functions = _functions(root)

    sims = [
        f.attrib["Name"]
        for f in functions.values()
        if f.attrib.get("Name", "").endswith("Simultaneo") and f.attrib["Type"] == "EFX"
    ]
    assert len(sims) >= 10  # seven wash shapes + three beam shapes
    for name in ("Movimientos Washes", "Movimientos Beams"):
        chaser = next(f for f in functions.values() if f.attrib.get("Name") == name)
        speed = find_local(chaser, "Speed")
        assert speed.attrib["FadeIn"] == "5000", name
        assert speed.attrib["FadeOut"] == "5000", name
        step_ids = {s.text for s in findall_local(chaser, "Step")}
        assert any(functions[sid].attrib["Name"].endswith("Simultaneo") for sid in step_ids), name
