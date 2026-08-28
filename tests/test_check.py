"""The checks, and one test per bug that has actually happened in the room.

This file is the discipline the show is now built on: **a malfunction is not
fixed until a check can see it**. Every regression below is a night that went
wrong - beams that stayed black, panels that were the right colour and off, a
room that went white when two levels were pressed - reproduced by putting the
bug back into a generated show and asserting the checker still bites.

The first test is the gate: every workspace the repo ships is run through every
rule. New rules therefore have to be true of all three shows at once, which is
what stops a check from being written to fit one file.
"""

from pathlib import Path

import pytest

from qlctool.checks.run import check_workspace
from qlctool.fixture_group import fixture_groups
from qlctool.library import FixtureLibrary
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, localname

REPO = Path(__file__).resolve().parents[3]
SHOWS = ("Vibra.qxw", "Vibra-beats.qxw", "Vibra-split.qxw")
BEAMS = (20, 21, 22, 23)

# Findings the shipped shows are allowed to carry. Empty, and meant to stay
# that way: an entry here is a known-broken button somebody will press.
KNOWN: set[tuple[str, str]] = set()


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


def _functions(workspace):
    return {
        function.attrib.get("Name"): function
        for function in find_local(workspace.root, "Engine")
        if localname(function) == "Function"
    }


def _show(name="Vibra-split.qxw"):
    return Workspace.load(REPO / "QLC+ Setups" / name)


def _rules(findings):
    return {(finding.rule, finding.function) for finding in findings}


@pytest.mark.parametrize("name", SHOWS)
def test_every_shipped_show_passes_every_check(name, library):
    """The gate. A rule that is not true of all three shows is not a rule."""
    findings = check_workspace(_show(name), library)
    unexpected = [f for f in findings if (f.rule, f.function) not in KNOWN]
    assert not unexpected, "\n".join(str(f) for f in unexpected)


def test_a_fixture_given_colour_with_nothing_opening_its_dimmer(library):
    """2026-08-26: the panels were the right colour and off all night.

    Reproduced by taking the master dimmer back out of the rig-wide colour
    scenes for the four panels - which is the shape the bug had, whatever is
    painting them: colour written, intensity left at zero.
    """
    workspace = _show()
    panels = {24, 25, 27, 28}
    for function in _functions(workspace).values():
        # The panels' own colour bank: they left the rig-wide wheel when they
        # started running their own programmes under AUTO.
        if function.attrib.get("Path") != "Colores PixelesLed":
            continue
        for value in findall_local(function, "FixtureVal"):
            if int(value.attrib["ID"]) not in panels or not value.text:
                continue
            numbers = [int(n) for n in value.text.split(",")]
            pairs = dict(zip(numbers[0::2], numbers[1::2], strict=True))
            pairs.pop(0, None)  # channel 1 is the panel's master dimmer
            value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "intensidad"
    ]
    assert findings, "colour with the dimmer left at zero went unnoticed"
    assert any("WX-60WPS" in fixture for f in findings for fixture in f.fixtures)


def test_a_colour_stated_on_a_fixture_left_running_its_own_programme(library):
    """2026-08-26: the panels have 42 built-in effects behind a mode channel.

    While that channel is in its automatic position the fixture ignores the
    red, green and blue it is sent, and nothing resets it on its own. A scene
    that states a colour and does not also stop the programme works or does
    not depending on what ran before it, which is the worst way to fail.
    """
    workspace = _show()
    panels = {24, 25, 27, 28}
    for function in _functions(workspace).values():
        if function.attrib.get("Type") != "Scene":
            continue
        for value in findall_local(function, "FixtureVal"):
            if int(value.attrib["ID"]) not in panels or not value.text:
                continue
            numbers = [int(n) for n in value.text.split(",")]
            pairs = dict(zip(numbers[0::2], numbers[1::2], strict=True))
            pairs.pop(5, None)  # channel 6 is the mode channel
            value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "programa interno"
    ]
    assert findings, "colour stated over a running programme went unnoticed"
    assert any("WX-60WPS" in fixture for f in findings for fixture in f.fixtures)


def test_the_panels_own_effects_are_actually_used(library):
    """The show drove four rather clever lights as four RGB cells for years."""
    workspace = _show()
    functions = _functions(workspace)
    assert "Ciclo Paneles" in functions
    effects = [n for n in functions if n.startswith("Paneles - ")]
    assert len(effects) == 42

    by_id = {f.attrib["ID"]: f for f in functions.values() if f.attrib.get("ID")}
    auto = {
        by_id[step.text].attrib["Name"]
        for step in findall_local(functions["AUTO"], "Step")
    }
    # Since 2026-08-28 the effects cycle sits inside `Ciclo Paneles Mixto`,
    # which alternates it with a manual phase listening to the rig wheel.
    assert "Ciclo Paneles Mixto" in auto, (
        "the panels animate themselves, unattended"
    )
    mixto_steps = {
        by_id[step.text].attrib["Name"]
        for step in findall_local(functions["Ciclo Paneles Mixto"], "Step")
    }
    assert "Ciclo Paneles" in mixto_steps, (
        "the effects phase left the panels' cycle"
    )


def test_a_group_whose_grid_does_not_match_the_lights_in_it(library):
    """2026-08-26: "la mitad de la barra led los pixeles leds estan apagados".

    Four wall panels and two eight-segment bars shared one 8x3 grid, and the
    panels only occupied four of its eight columns - so they were dark through
    the first half of every Fill. The grid also had four empty cells, and
    Cabezas declared 8x1 over twelve heads with four of them outside it.
    """
    workspace = _show()
    group = next(
        g for g in workspace.root.iter()
        if g.tag.endswith("FixtureGroup") and g.attrib.get("ID") == "0"
    )
    size = find_local(group, "Size")
    size.set("Y", str(int(size.attrib["Y"]) + 1))  # a row nothing lives in

    findings = [f for f in check_workspace(workspace, library) if f.rule == "rejilla"]
    assert findings, "a grid with a row of empty cells went unnoticed"
    assert "BarrasLed" in {f.function for f in findings}


def test_a_look_that_never_writes_the_wheel_coloured_fixtures(library):
    """2026-08-26: BLANCO TOTAL left the four 7R black.

    They have no red channel, so every generator that reasons in RGB skipped
    them silently - not dimmed, never written to.
    """
    workspace = _show()
    functions = _functions(workspace)
    for name in ("Blanco Total", "Flash 100%", "Flash 50%"):
        scene = functions[name]
        for value in findall_local(scene, "FixtureVal"):
            if int(value.attrib["ID"]) in BEAMS:
                scene.remove(value)

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "rueda de color" and f.function == "Blanco Total"
    ]
    assert findings, "a rig-wide white that skips the beams went unnoticed"
    assert all("BEAM" in fixture for fixture in findings[0].fixtures)


def test_two_programmes_writing_one_fixtures_colour(library):
    """2026-08-25: the room went white with two colour beds on one rig.

    Reproduced the way the owner hit it: put a pixel fixture back into the
    rig-wide colour scene while the same wheel step's matrix is painting it.
    """
    workspace = _show()
    functions = _functions(workspace)
    scene = functions["Rig Rojo"]
    value = find_local(scene, "FixtureVal")
    # Fixture 2 is an LED Bar: pure RGB, and painted by the step's matrix.
    duplicate = value.makeelement(value.tag, {"ID": "2"})
    duplicate.text = "0,255,1,0,2,0"
    scene.append(duplicate)

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "colores pisados"
    ]
    assert any(f.function.startswith("Rig Rojo") for f in findings), (
        "two colour sources on one bar went unnoticed"
    )


def test_two_colour_clocks_ticking_in_one_room_state(library):
    """2026-08-26: "las barras led van con los colores a su bola, no siguen el show".

    The rig-wide wheel stepped the room through cyan while the bars' own matrix
    cycle stepped them through magenta, and both were right alone: two chasers
    that each rotate colour on their own clock never agree. The bars' colour
    now rides inside the wheel's steps - a matrix of the step's own colour -
    and the bug is reproduced by stepping the standalone cycle back into AUTO
    beside the wheel, which is exactly the shape the show used to have.
    """
    workspace = _show()
    functions = _functions(workspace)
    auto = functions["AUTO"]
    cycle = functions["Ciclo Matrices BarrasLed"]
    step = auto.makeelement(findall_local(auto, "Step")[0].tag, {"Number": "99"})
    step.text = cycle.attrib["ID"]
    auto.append(step)

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "relojes de color"
    ]
    assert findings, "two colour clocks in one room state went unnoticed"
    assert any("LED Bar" in fixture for f in findings for fixture in f.fixtures)


def test_the_curated_matrix_library_never_reaches_a_wheel_step(library):
    """Task 5's ten curated scripts (Sine Wave, Marquee, Gradient, ...) are
    library material and per-group Ciclo Matrices only - `Rueda Colores`'s
    steps still start only the single-wheel-colour matrices
    `generate_pixel_wheel_matrices` builds (rule `relojes de color`'s whole
    premise: a wheel step states exactly one colour clock)."""
    workspace = _show()
    curated_names = {
        "Sine Wave", "Lines", "Marquee", "Plasma",
        "One By One", "Fill Unfill", "Noise",
        "Circular", "3D Starfield", "Gradient",
    }
    wheel_matrices = [
        function
        for function in _functions(workspace).values()
        if function.attrib.get("Type") == "RGBMatrix"
        and function.attrib.get("Path") == "Colores Rig"
    ]
    assert wheel_matrices, "no wheel-step matrices found to check"
    for matrix in wheel_matrices:
        algorithm = find_local(matrix, "Algorithm")
        name = None if algorithm.attrib["Type"] == "Plain" else (algorithm.text or "").strip()
        # The one deliberate exception (2026-08-28): the multicolour steps
        # state many colours by design, and their pixel companion is the
        # rainbow plasma - still on the wheel's clock, so still one clock.
        if "Plasma Rainbow (Rueda)" in (matrix.attrib.get("Name") or ""):
            continue
        assert name not in curated_names, (
            f"{matrix.attrib.get('Name')} is a curated matrix on a wheel step"
        )


def test_a_dimmer_at_full_behind_a_shut_shutter(library):
    """A BEAM 230W 7R at DMX 0 on its shutter is shut, dimmer or no dimmer."""
    workspace = _show()
    scene = _functions(workspace)["Blanco Total"]
    for value in findall_local(scene, "FixtureVal"):
        if int(value.attrib["ID"]) not in BEAMS:
            continue
        numbers = [int(n) for n in value.text.split(",")]
        pairs = dict(zip(numbers[0::2], numbers[1::2], strict=True))
        pairs[5] = 0  # the shutter channel, closed
        value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "intensidad" and f.function == "Blanco Total"
    ]
    assert findings, "a shut shutter with the dimmer at full went unnoticed"


def test_a_shutter_whose_open_position_is_zero_is_left_alone(library):
    """The other half of the same rule, and the reason it needs the range.

    A CLB2.4 head labels DMX 0 "no strobe": untouched, it is already open.
    Reporting it would bury the real ones under two hundred false alarms.
    """
    findings = check_workspace(_show(), library)
    assert not [
        f for f in findings
        if f.rule == "intensidad" and any("CLB2.4" in n for n in f.fixtures)
    ]


def test_a_master_in_the_same_solo_frame_as_what_it_starts(library):
    """The bug that killed AUTO the instant it was pressed."""
    workspace = _show()
    functions = _functions(workspace)
    auto = functions["AUTO"].attrib["ID"]
    wheel = functions["Rueda Colores"].attrib["ID"]

    console = find_local(workspace.root, "VirtualConsole")
    for frame in console.iter():
        if localname(frame) != "SoloFrame":
            continue
        buttons = [b for b in frame if localname(b) == "Button"]
        if not buttons or find_local(buttons[0], "Function").attrib["ID"] != auto:
            continue
        find_local(buttons[1], "Function").set("ID", wheel)
        break

    findings = [f for f in check_workspace(workspace, library) if f.rule == "consola"]
    assert any(f.function == "AUTO" for f in findings), (
        "AUTO sharing a solo frame with its own member went unnoticed"
    )


def test_two_buttons_on_the_same_key(library):
    """Every widget sees every key press, so a shared letter fires both."""
    workspace = _show()
    console = find_local(workspace.root, "VirtualConsole")
    for button in console.iter():
        if localname(button) != "Button":
            continue
        key = find_local(button, "Key")
        if key is not None and key.text == "J":
            key.text = "Q"
            break

    findings = [f for f in check_workspace(workspace, library) if f.rule == "consola"]
    assert any("tecla" in f.message for f in findings)


def test_a_widget_that_spills_past_its_own_parent_frame(library):
    """2026-08-27: the librería's Matrices frame grew to 34 buttons on a
    6-column, 300px-tall layout sized for 30 (Task 5's curated scripts). The
    sixth row rendered 20px past the frame's own bottom edge, into the
    sibling "Ruedas y ciclos" frame below it - and `qlctool check` said
    nothing, because `_off_canvas` only compares a widget's absolute position
    against the outer 1440x900 canvas, never against the frame that actually
    contains it.

    The shipped shape is fixed first (asserted below); a widget pushed past
    its own parent's box reproduces the original bug's shape and the new
    check must bite on it, wherever it happens.
    """
    workspace = _show()
    findings = [f for f in check_workspace(workspace, library) if f.rule == "consola"]
    assert not [f for f in findings if "su propio marco" in f.message], (
        "the shipped console already spills a widget past a parent frame"
    )

    console = find_local(workspace.root, "VirtualConsole")
    matrix_frame = next(
        frame for frame in console.iter()
        if localname(frame) == "SoloFrame"
        and frame.attrib.get("Caption", "").startswith("Matrices")
    )
    frame_height = int(find_local(matrix_frame, "WindowState").attrib["Height"])
    button = next(b for b in matrix_frame if localname(b) == "Button")
    # Push it mostly past the frame's own bottom edge - the exact shape of
    # the original overflow, just forced rather than incidental.
    find_local(button, "WindowState").set("Y", str(frame_height - 10))

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "consola" and "su propio marco" in f.message
    ]
    assert findings, "a widget pushed past its own parent frame's box went unnoticed"


def test_an_animation_the_chaser_cuts_off_before_it_finishes(library):
    """2026-08-26: "empezamos una animacion pero nunca la terminamos".

    A Fill over an eight-wide bar is eight frames; the cycle held each matrix
    for four of them, so the bar lit half way, jumped to another colour, and
    lit half way again, all night. Cutting an animation in its first half is
    also half of why the pixels read as off.
    """
    workspace = _show()
    cycle = _functions(workspace)["Ciclo Matrices BarrasLed"]
    for step in findall_local(cycle, "Step"):
        step.set("Hold", "2000")  # the flat interval it used to have

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "efecto cortado"
    ]
    assert findings, "a chaser cutting its own animations went unnoticed"
    assert "Ciclo Matrices BarrasLed" in {f.function for f in findings}


def test_a_strobe_left_running_as_one_step_of_a_cycle(library):
    """2026-08-26: the other half of "los pixeles la mitad del tiempo apagados".

    This show's own rule is that a strobe is for somebody standing at the
    laptop. Six Strobe matrices sitting among the steps of a cycle that loops
    all night is that rule broken quietly.
    """
    workspace = _show()
    functions = _functions(workspace)
    cycle = functions["Ciclo Matrices BarrasLed"]
    strobe = functions["BarrasLed - Strobe Rojo"]
    step = cycle.makeelement(findall_local(cycle, "Step")[0].tag, {
        "Number": "99", "FadeIn": "0", "Hold": "2000", "FadeOut": "0",
    })
    step.text = strobe.attrib["ID"]
    cycle.append(step)

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "estrobo en un ciclo"
    ]
    assert findings, "a strobe among a cycle's steps went unnoticed"


def test_the_beams_take_their_colour_from_one_group_only(library):
    """2026-08-26: `Rueda Mezcla` started two wheels that both coloured them.

    The four 7R were in the BarrasLed group purely so its third row existed for
    the matrices - and a matrix does nothing on a fixture with no RGB anyway.
    Being in the group also put them in its colour bank, so the bars' mix wheel
    and the heads' mix wheel wrote their colour wheel at the same time.
    """
    workspace = _show()
    groups = {
        group.name: group for group in fixture_groups(workspace.root)
    }
    assert not set(BEAMS) & set(groups["BarrasLed"].fixture_ids)
    assert set(BEAMS) <= set(groups["Cabezas"].fixture_ids)


def test_a_smoke_machine_swept_into_somebody_elses_scene(library):
    """A pump caught in an "all dimmers up" scene runs until the tank is dry."""
    workspace = _show()
    scene = _functions(workspace)["Blanco Total"]
    value = find_local(scene, "FixtureVal")
    # Fixture 26 is a Generic Smoke: sweep its pump up with everything else.
    duplicate = value.makeelement(value.tag, {"ID": "26"})
    duplicate.text = "0,255"
    scene.append(duplicate)

    findings = [f for f in check_workspace(workspace, library) if f.rule == "humo"]
    assert any(f.function == "Blanco Total" for f in findings)


def test_a_strobe_flashing_faster_than_four_hertz(library):
    """2026-08-27, Codex review of the highlight plan: `Strobo Rapido` had
    shipped alternating the whole rig between white and black every 50 ms -
    ten flashes a second, inside the photosensitive-epilepsy trigger band -
    and the checker said "ningun problema". Reproduced by putting the 50 ms
    steps back into the burst.
    """
    workspace = _show()
    chaser = _functions(workspace)["Strobo Rapido"]
    for step in findall_local(chaser, "Step"):
        step.set("Hold", "50")
    find_local(chaser, "Speed").set("Duration", "50")

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "estrobo demasiado rapido"
    ]
    assert findings, "a 10 Hz whole-rig strobe went unnoticed"
    assert "Strobo Rapido" in {f.function for f in findings}


def test_a_strobe_that_loops_behind_a_button(library):
    """2026-08-27, same review: the console's STROBO was a Toggle over a
    looping chaser - one press and the rig flashed until somebody remembered
    which button had started it. A strobe hit has to be a bounded SingleShot
    burst that ends itself. Reproduced by putting the loop back.
    """
    workspace = _show()
    chaser = _functions(workspace)["Strobo Rapido"]
    find_local(chaser, "RunOrder").text = "Loop"

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "estrobo enganchado"
    ]
    assert findings, "a latched looping strobe went unnoticed"
    assert "Strobo Rapido" in {f.function for f in findings}


def test_a_flash_that_lights_the_room_without_strobing_it(library):
    """2026-08-27, the owner testing at home over the FT232R card: "esto no
    hace estrobo y antes lo hacia cuando le daba al espacio". The hand-built
    `Flash 100%` drove every shutter near the top of its range; the generated
    one was a steady work light with the shutters parked "Open". Reproduced
    by parking the CromoWash strobe channel back on its "No function" value.
    """
    workspace = _show()
    scene = _functions(workspace)["Flash 100%"]
    for value in findall_local(scene, "FixtureVal"):
        if int(value.attrib["ID"]) not in (0, 1, 13, 14):
            continue
        numbers = [int(n) for n in value.text.split(",")]
        pairs = dict(zip(numbers[0::2], numbers[1::2], strict=True))
        pairs[10] = 4  # the strobe channel, 0-9 = "No function"
        value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "flash sin estrobo"
    ]
    assert findings, "a flash with its shutters parked open went unnoticed"
    assert "Flash 100%" in {f.function for f in findings}


def test_a_strobe_scene_that_skips_half_the_rig(library):
    """2026-08-27, found in the same session: `Strobo ON` drove only the
    channels with a labelled strobing range, so the seven Vortex PARs and the
    pixel panels - bare speed channels, no labels - held steady while the
    rest of the rig flashed. Reproduced by dropping the Vortex writes back
    out of the scene.
    """
    workspace = _show()
    scene = _functions(workspace)["Strobo ON"]
    for value in findall_local(scene, "FixtureVal"):
        if int(value.attrib["ID"]) in range(6, 13):
            scene.remove(value)

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "estrobo incompleto"
    ]
    assert findings, "a strobe scene skipping seven fixtures went unnoticed"
    assert "Strobo ON" in {f.function for f in findings}


def test_a_strobe_the_music_can_fire(library):
    """2026-08-27: the bass bar presses `Golpe Graves`, the deliberately
    plain twin of the flash, because a strobe fired by whatever the PA does
    is a strobe nobody chose. Reproduced by giving that scene the strobe
    values back.
    """
    workspace = _show()
    scene = _functions(workspace)["Golpe Graves"]
    for value in findall_local(scene, "FixtureVal"):
        if int(value.attrib["ID"]) not in (0, 1, 13, 14):
            continue
        numbers = [int(n) for n in value.text.split(",")]
        pairs = dict(zip(numbers[0::2], numbers[1::2], strict=True))
        pairs[10] = 218  # the strobe channel, strobing
        value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "estrobo en manos del audio"
    ]
    assert findings, "an audio-fired strobe went unnoticed"
    assert "Golpe Graves" in {f.function for f in findings}


def test_a_flash_button_pointed_at_something_qlcplus_cannot_flash(library):
    """2026-08-27: only a Scene implements flash (`Scene::flash`; the base
    class raises a flag nothing reads). A Flash button over a Chaser, EFX or
    Collection half-works and teaches the operator not to trust the console.
    Reproduced by pointing the FLASH button at the AUTO Collection.
    """
    workspace = _show()
    functions = _functions(workspace)
    auto_id = functions["AUTO"].attrib["ID"]
    for button in workspace.root.iter():
        if localname(button) != "Button":
            continue
        action = find_local(button, "Action")
        if action is None or (action.text or "").strip() != "Flash":
            continue
        find_local(button, "Function").set("ID", auto_id)
        break

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "flash sin escena"
    ]
    assert findings, "a Flash button over a Collection went unnoticed"


def test_a_quiet_dimmer_shadowed_by_a_full_one_running_beside_it(library):
    """2026-08-27, the finding that sank the first Ambiente plan: intensity
    mixes HTP, so while the colour wheel held every dimmer at 255 all night, a
    quiet level asking for 110 on the same channels changed nothing - and
    nothing looked broken. Reproduced by giving the wheel's scenes their
    dimmers back.
    """
    from qlctool import roles
    from qlctool.capabilities_of import capabilities_of

    workspace = _show()
    caps = {
        c.fixture.fixture_id: c
        for c in capabilities_of(workspace.root, library)
    }
    for function in _functions(workspace).values():
        if function.attrib.get("Type") != "Scene":
            continue
        if not function.attrib.get("Name", "").startswith("Rig "):
            continue
        for value in findall_local(function, "FixtureVal"):
            fixture_id = int(value.attrib["ID"])
            offsets = caps[fixture_id].offsets_for_role(roles.DIMMER)
            if not offsets or not value.text:
                continue
            numbers = [int(n) for n in value.text.split(",")]
            pairs = dict(zip(numbers[0::2], numbers[1::2], strict=True))
            pairs.update({offset: 255 for offset in offsets})
            value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "intensidad tapada"
    ]
    assert findings, "a dimmer nobody can ever see went unnoticed"


def test_a_flash_accent_on_a_wheel_no_state_puts_back(library):
    """2026-08-27: wheel channels are LTP - the last write stays. A Flash
    scene that moves the beams' colour wheel releases cleanly only if the
    state underneath also drives that wheel; otherwise the accent's position
    simply stays, and nobody can say which button left it there. Reproduced
    by taking the beams' white out of `Momento Charla`.
    """
    workspace = _show()
    functions = _functions(workspace)
    charla = functions["Momento Charla"]
    white_id = functions["Color Beam - White"].attrib["ID"]
    for step in findall_local(charla, "Step"):
        if step.text == white_id:
            charla.remove(step)

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "acento sin dueño"
    ]
    assert findings, "a flashed wheel with no owner underneath went unnoticed"


def test_an_efx_stretched_over_both_optics_families(library):
    """2026-08-27: all twelve movers ran the same 100x100 EFX - a wash's wide
    soft curve is a 7R needle dragged through faces at the same size and
    speed. A mover with a gobo wheel is beam-class; an EFX that mixes the
    families is tuned for neither. Reproduced by adding a beam to a wash EFX.
    """
    from lxml import etree

    from qlctool.constants import QLC_NS

    workspace = _show()
    efx = next(
        f for f in _functions(workspace).values()
        if f.attrib.get("Type") == "EFX"
        and f.attrib.get("Name", "").startswith("Wash ")
    )
    fixture = etree.SubElement(efx, f"{{{QLC_NS}}}Fixture")
    for tag, text in (("ID", "20"), ("Head", "0"), ("Mode", "0"),
                      ("Direction", "Forward"), ("StartOffset", "0")):
        child = etree.SubElement(fixture, f"{{{QLC_NS}}}{tag}")
        child.text = text

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "familias de movimiento mezcladas"
    ]
    assert findings, "an EFX mixing washes and beams went unnoticed"


def test_an_audio_trigger_with_no_bar_bound_to_anything(library):
    """2026-08-27, Codex audit verification (docs/superpowers/plans/
    2026-08-27-qlc-audit-verification.md, claim A1): the console's
    AudioTriggers widget ships with BarsNumber=5 and zero SpectrumBar
    children. Somebody who finds it and picks an audio input in
    Configuration still presses nothing - every band is unbound, so the
    widget is dead by design, not by missing hardware. Reproduced by
    stripping every SpectrumBar off the widget.
    """
    workspace = _show()
    widget = next(
        w for w in workspace.root.iter() if localname(w) == "AudioTriggers"
    )
    for bar in findall_local(widget, "SpectrumBar"):
        widget.remove(bar)

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "disparador de audio vacio"
    ]
    assert findings, "an AudioTriggers widget with no bound bar went unnoticed"


def test_an_audio_trigger_bound_to_a_strobe(library):
    """Same audit: an audio bar presses whatever widget it is bound to on the
    way up and again on the way down, with no finger on the button and no
    limit on how often a beat repeats it. A strobe behind that is worse than
    the latched Toggle the 2026-08-27 review already found, because nobody
    even pressed it. Reproduced by binding a bar to the button that starts
    `Strobo Rapido`.
    """
    from lxml import etree

    from qlctool.constants import QLC_NS

    workspace = _show()
    functions = _functions(workspace)
    strobe_id = functions["Strobo Rapido"].attrib["ID"]
    strobe_button = next(
        b for b in workspace.root.iter()
        if localname(b) == "Button"
        and (function := find_local(b, "Function")) is not None
        and function.attrib.get("ID") == strobe_id
    )
    widget = next(
        w for w in workspace.root.iter() if localname(w) == "AudioTriggers"
    )
    bar = etree.SubElement(widget, f"{{{QLC_NS}}}SpectrumBar")
    bar.set("Name", "Graves")
    bar.set("Type", "3")
    bar.set("MinThreshold", "12")
    bar.set("MaxThreshold", "51")
    bar.set("Divisor", "1")
    bar.set("Index", "0")
    bar.set("WidgetID", strobe_button.attrib["ID"])

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "disparador de audio vacio"
    ]
    assert findings, "an audio bar bound to a strobe went unnoticed"


def test_an_audio_trigger_bound_to_a_room_state_button(library):
    """2026-08-27, controller review of this same audit: the first fix bound
    the bass bar to `Blanco Total`, a Scene with no strobe in it - but that
    scene's button lives in the room-state SoloFrame alongside AUTO.
    `VCSoloFrame::slotWidgetFunctionStarting` stops every other widget's
    function in the frame the moment one starts (confirmed against
    `ui/src/virtualconsole/vcbutton.cpp` and `vcaudiotriggers.cpp` in the
    QLC+ source), and nothing restarts AUTO when the bar releases on the way
    back down - a human choosing to press that button is the frame doing its
    job; a bass line doing it unattended is a malfunction. Reproduced by
    binding a bar to `Blanco Total`'s own button, the shape the shipped fix
    briefly had. The replacement - a bar bound to the `Flash 100%` hit, a
    plain-frame Flash button outside any SoloFrame - must not trip this
    finding.
    """
    from lxml import etree

    from qlctool.constants import QLC_NS

    workspace = _show()
    functions = _functions(workspace)

    def button_for(name):
        function_id = functions[name].attrib["ID"]
        return next(
            b for b in workspace.root.iter()
            if localname(b) == "Button"
            and (function := find_local(b, "Function")) is not None
            and function.attrib.get("ID") == function_id
        )

    widget = next(
        w for w in workspace.root.iter() if localname(w) == "AudioTriggers"
    )

    def bind(widget_id):
        for bar in findall_local(widget, "SpectrumBar"):
            widget.remove(bar)
        bar = etree.SubElement(widget, f"{{{QLC_NS}}}SpectrumBar")
        bar.set("Name", "Graves")
        bar.set("Type", "3")
        bar.set("MinThreshold", "12")
        bar.set("MaxThreshold", "51")
        bar.set("Divisor", "1")
        bar.set("Index", "0")
        bar.set("WidgetID", widget_id)

    bind(button_for("Blanco Total").attrib["ID"])
    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "disparador de audio vacio"
    ]
    assert findings, "an audio bar pressing a room-state button went unnoticed"

    bind(button_for("Flash 100%").attrib["ID"])
    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "disparador de audio vacio"
    ]
    assert not findings, "the fixed binding (Flash 100%) should not trip this rule"


def test_an_audio_trigger_bar_bound_to_a_dangling_widget_id(library):
    """2026-08-27, final whole-branch review of this same audit: `_is_bound`
    counted any WidgetID as a binding, even one no widget on the console
    actually carries. QLC+'s own `checkWidgetFunctionality` looks the widget
    up by ID first and does nothing when that lookup fails
    (qmlui/virtualconsole/vcaudiotriggers.cpp:506) - so a bar left pointing
    at a deleted or never-created widget presses nothing, exactly like a bar
    with no WidgetID at all, and an AudioTriggers widget whose only bar does
    this is dead by construction, the same finding as the empty-BarsNumber
    case above. Reproduced by pointing the one bar QLC+ ships at a WidgetID
    nothing on the console carries.
    """
    from lxml import etree

    from qlctool.constants import QLC_NS

    workspace = _show()
    widget = next(
        w for w in workspace.root.iter() if localname(w) == "AudioTriggers"
    )
    for bar in findall_local(widget, "SpectrumBar"):
        widget.remove(bar)
    bar = etree.SubElement(widget, f"{{{QLC_NS}}}SpectrumBar")
    bar.set("Name", "Graves")
    bar.set("Type", "3")
    bar.set("MinThreshold", "12")
    bar.set("MaxThreshold", "51")
    bar.set("Divisor", "1")
    bar.set("Index", "0")
    bar.set("WidgetID", "999999")

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "disparador de audio vacio"
    ]
    assert findings, "a bar bound to a dangling WidgetID went unnoticed"


def test_a_flashed_strobe_no_state_switches_off(library):
    """2026-08-28: the owner pressed FLASH and the four panels strobed until
    somebody found `Strobo OFF` by hand. Strobe channels are LTP and a
    released Flash restores nothing, so every room state that lights the
    fixture must itself write the strobe channel back off. Reproduced by
    taking the strobe-off write out of every scene that has it on the panels.
    """
    workspace = _show()
    panels = {24, 25, 27, 28}
    for function in _functions(workspace).values():
        if function.attrib.get("Type") != "Scene":
            continue
        for value in findall_local(function, "FixtureVal"):
            if int(value.attrib["ID"]) not in panels or not value.text:
                continue
            numbers = [int(n) for n in value.text.split(",")]
            pairs = dict(zip(numbers[0::2], numbers[1::2], strict=True))
            if pairs.get(4) == 0:  # channel 5 is the strobe, 0 stops it
                pairs.pop(4)
            value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "estrobo pegado"
    ]
    assert findings, "a flashed strobe nobody switches off went unnoticed"
    assert any("WX-60WPS" in fixture for f in findings for fixture in f.fixtures)


def test_the_wheel_colours_the_panels_and_the_mixto_owns_their_mode(library):
    """2026-08-28: the panels join the rig's colours without a second clock.

    The rig wheel writes their RGB on every step - never their mode channel -
    and `Ciclo Paneles Mixto` alternates them between their own programmes and
    manual listening. One colour clock, one mode owner. This pins the wiring:
    lose either half and the panels are back to "a su bola" or to ignoring
    every colour they are sent.
    """
    workspace = _show()
    functions = _functions(workspace)
    panels = {24, 25, 27, 28}

    mixto = functions["Ciclo Paneles Mixto"]
    steps = [s.text for s in findall_local(mixto, "Step")]
    step_names = {
        f.attrib.get("Name")
        for f in functions.values()
        if f.attrib.get("ID") in steps
    }
    assert step_names == {"Ciclo Paneles", "Paneles Manual"}

    rig_scenes = [
        f for name, f in functions.items()
        if name and name.startswith(("Rig ", "Cabezas "))
        and f.attrib.get("Type") == "Scene"
        and f.attrib.get("Path") == "Colores Rig"
    ]
    assert rig_scenes
    for scene in rig_scenes:
        written_panels = set()
        for value in findall_local(scene, "FixtureVal"):
            if int(value.attrib["ID"]) not in panels or not value.text:
                continue
            written_panels.add(int(value.attrib["ID"]))
            numbers = [int(n) for n in value.text.split(",")]
            offsets = set(numbers[0::2])
            assert {1, 2, 3} <= offsets, scene.attrib.get("Name")  # RGB
            assert 5 not in offsets, scene.attrib.get("Name")  # mode is owned
        assert written_panels == panels, scene.attrib.get("Name")


def test_colour_on_the_panels_without_a_mode_owner_still_fires(library):
    """2026-08-28: the `programa interno` excuse is ownership, not amnesty.

    The rig scenes state RGB on the panels without the mode-off because every
    room state that lights them runs `Ciclo Paneles Mixto`, which owns the
    mode channel. Take the mode write out of the owner's own scenes - the
    panels' effect scenes and `Paneles Manual` - and the old bug is back:
    colour that works or not depending on what ran before. The rule must bite
    again, or the excuse is amnesty rather than ownership.
    """
    workspace = _show()
    functions = _functions(workspace)
    panels = {24, 25, 27, 28}
    for name, function in functions.items():
        if not (name or "").startswith("Paneles"):
            continue
        for value in findall_local(function, "FixtureVal"):
            if int(value.attrib["ID"]) not in panels or not value.text:
                continue
            numbers = [int(n) for n in value.text.split(",")]
            pairs = dict(zip(numbers[0::2], numbers[1::2], strict=True))
            pairs.pop(5, None)  # channel 6 is the mode channel
            value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))

    findings = [
        f for f in check_workspace(workspace, library)
        if f.rule == "programa interno"
    ]
    assert findings, "colour with no standing mode owner went unnoticed"
    assert any("WX-60WPS" in fixture for f in findings for fixture in f.fixtures)
