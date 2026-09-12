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

import re
from pathlib import Path

import pytest

from qlctool import roles
from qlctool.audience_window import BEAM_WINDOW
from qlctool.capabilities_of import capabilities_of
from qlctool.checks.console_states import room_states
from qlctool.checks.rule_pick_darkens import check_pick_darkens
from qlctool.checks.rule_undeclared_heads import check_undeclared_heads
from qlctool.checks.run import check_workspace
from qlctool.checks.show_graph import (
    build_show_graph,
    group_fixtures,
    lit,
    reach,
)
from qlctool.checks.strobe_written import strobe_capable_offsets
from qlctool.fixture_group import fixture_groups
from qlctool.fog_offsets import fog_offsets
from qlctool.generate.canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, iter_local, localname

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


def _twin_scene(workspace, functions, source_name, twin_name):
    """A copy of a scene under a new id: the old burst chasers' white/black."""
    import copy

    from qlctool.ids import next_function_id

    twin = copy.deepcopy(functions[source_name])
    twin.set("ID", str(next_function_id(workspace.root)))
    twin.set("Name", twin_name)
    workspace.add_function(twin)
    return twin


def _strip_strobe_writes_from_black_twin(black, capabilities):
    """Make a Todo Negro twin model the old Intensity-only black step."""
    for value in list(findall_local(black, "FixtureVal")):
        fixture_id = int(value.attrib["ID"])
        capability = capabilities.get(fixture_id)
        assert capability is not None, f"black twin fixture {fixture_id} has no capability"
        pairs = _pairs_of(value)
        for offset in capability.offsets_for_role(roles.STROBE):
            pairs.pop(offset, None)
        if pairs:
            _write_pairs(value, pairs)
        else:
            value.getparent().remove(value)

    intensity_writes = 0
    for value in findall_local(black, "FixtureVal"):
        fixture_id = int(value.attrib["ID"])
        capability = capabilities[fixture_id]
        for offset, level in _pairs_of(value).items():
            assert capability.roles_by_offset[offset] != roles.STROBE, (
                f"black twin still writes a shutter/strobe on fixture {fixture_id}"
            )
            if capability.groups_by_offset[offset] == "Intensity":
                assert level == 0, (
                    f"black twin writes lit Intensity channel {offset} on fixture {fixture_id}"
                )
                intensity_writes += 1
    assert intensity_writes, "black twin lost every zero-valued Intensity darkness claim"


def _burst_chaser(workspace, library, hold=125):
    """Put the pre-2026-09-02 STROBO back: a white/black chaser on a Toggle.

    `Strobo Rapido` was a SingleShot chaser alternating a white scene and a
    black one, on a Toggle button on the show page. It is a held shutter scene
    now, so the tests that need a strobe-shaped chaser build the old one here:
    twins of `Golpe Graves` (white, shutters open) and `Todo Negro`.
    """

    from qlctool.functions.chaser import build_chaser
    from qlctool.ids import next_function_id
    from qlctool.vc.button import build_button
    from qlctool.vc.widget_ids import next_widget_id

    functions = _functions(workspace)
    capabilities = {
        capability.fixture.fixture_id: capability
        for capability in capabilities_of(workspace.root, library)
    }
    white = _twin_scene(workspace, functions, "Golpe Graves", "Rafaga Blanco")
    black = _twin_scene(workspace, functions, "Todo Negro", "Rafaga Negro")
    _strip_strobe_writes_from_black_twin(black, capabilities)
    chaser_id = next_function_id(workspace.root)
    chaser = build_chaser(
        chaser_id,
        "Rafaga",
        [int(white.attrib["ID"]), int(black.attrib["ID"])] * 4,
        hold=hold,
        run_order="SingleShot",
        path="Strobos",
    )
    workspace.add_function(chaser)
    hits = next(
        f
        for f in workspace.root.iter()
        if localname(f) == "Frame" and f.attrib.get("Caption", "").startswith("GOLPES")
    )
    button = build_button(
        hits, next_widget_id(workspace.root), "RAFAGA", chaser_id, x=8, y=30, width=60, height=40
    )
    return chaser, button


@pytest.mark.parametrize("name", SHOWS)
def test_every_shipped_show_passes_every_check(name, library):
    """The gate. A rule that is not true of all three shows is not a rule."""
    findings = check_workspace(_show(name), library)
    unexpected = [f for f in findings if (f.rule, f.function) not in KNOWN]
    assert not unexpected, "\n".join(str(f) for f in unexpected)


def test_a_fixture_given_colour_with_nothing_opening_its_dimmer(library):
    """2026-08-26: the panels were the right colour and off all night.

    Reproduced by taking the master dimmer back out of the scenes that open
    it under AUTO - the panels' own programme and manual phases - which is the
    shape the bug had, whatever is painting them: colour written, intensity
    left at zero. (The colour banks used to be the target; since 2026-09-02
    they are held colour-only layers and own no dimmer at all.)
    """
    workspace = _show()
    panels = {24, 25, 27, 28}
    for name, function in _functions(workspace).items():
        if not (name.startswith("Paneles - ") or name == "Paneles Manual"):
            continue
        for value in findall_local(function, "FixtureVal"):
            if int(value.attrib["ID"]) not in panels or not value.text:
                continue
            numbers = [int(n) for n in value.text.split(",")]
            pairs = dict(zip(numbers[0::2], numbers[1::2], strict=True))
            pairs.pop(0, None)  # channel 1 is the panel's master dimmer
            value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))

    findings = [f for f in check_workspace(workspace, library) if f.rule == "intensidad"]
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

    findings = [f for f in check_workspace(workspace, library) if f.rule == "programa interno"]
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
    auto = {by_id[step.text].attrib["Name"] for step in findall_local(functions["AUTO"], "Step")}
    # Since 2026-08-28 the effects cycle sits inside `Ciclo Paneles Mixto`,
    # which alternates it with a manual phase listening to the rig wheel.
    assert "Ciclo Paneles Mixto" in auto, "the panels animate themselves, unattended"
    mixto_steps = {
        by_id[step.text].attrib["Name"]
        for step in findall_local(functions["Ciclo Paneles Mixto"], "Step")
    }
    assert "Ciclo Paneles" in mixto_steps, "the effects phase left the panels' cycle"


def test_a_group_whose_grid_does_not_match_the_lights_in_it(library):
    """2026-08-26: "la mitad de la barra led los pixeles leds estan apagados".

    Four wall panels and two eight-segment bars shared one 8x3 grid, and the
    panels only occupied four of its eight columns - so they were dark through
    the first half of every Fill. The grid also had four empty cells, and
    Cabezas declared 8x1 over twelve heads with four of them outside it.
    """
    workspace = _show()
    group = next(
        g
        for g in workspace.root.iter()
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
        f
        for f in check_workspace(workspace, library)
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

    findings = [f for f in check_workspace(workspace, library) if f.rule == "colores pisados"]
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

    findings = [f for f in check_workspace(workspace, library) if f.rule == "relojes de color"]
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
        "Sine Wave",
        "Lines",
        "Marquee",
        "Plasma",
        "One By One",
        "Fill Unfill",
        "Noise",
        "Circular",
        "3D Starfield",
        "Gradient",
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
        f
        for f in check_workspace(workspace, library)
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
        f for f in findings if f.rule == "intensidad" and any("CLB2.4" in n for n in f.fixtures)
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
        frame
        for frame in console.iter()
        if localname(frame) == "SoloFrame"
        and frame.attrib.get("Caption", "").startswith("Matrices")
    )
    frame_height = int(find_local(matrix_frame, "WindowState").attrib["Height"])
    button = next(b for b in matrix_frame if localname(b) == "Button")
    # Push it mostly past the frame's own bottom edge - the exact shape of
    # the original overflow, just forced rather than incidental.
    find_local(button, "WindowState").set("Y", str(frame_height - 10))

    findings = [
        f
        for f in check_workspace(workspace, library)
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

    findings = [f for f in check_workspace(workspace, library) if f.rule == "efecto cortado"]
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
    step = cycle.makeelement(
        findall_local(cycle, "Step")[0].tag,
        {
            "Number": "99",
            "FadeIn": "0",
            "Hold": "2000",
            "FadeOut": "0",
        },
    )
    step.text = strobe.attrib["ID"]
    cycle.append(step)

    findings = [f for f in check_workspace(workspace, library) if f.rule == "estrobo en un ciclo"]
    assert findings, "a strobe among a cycle's steps went unnoticed"


def test_the_beams_take_their_colour_from_one_group_only(library):
    """2026-08-26: `Rueda Mezcla` started two wheels that both coloured them.

    The four 7R were in the BarrasLed group purely so its third row existed for
    the matrices - and a matrix does nothing on a fixture with no RGB anyway.
    Being in the group also put them in its colour bank, so the bars' mix wheel
    and the heads' mix wheel wrote their colour wheel at the same time.
    """
    workspace = _show()
    groups = {group.name: group for group in fixture_groups(workspace.root)}
    assert not set(BEAMS) & set(groups["BarrasLed"].fixture_ids)
    assert set(BEAMS) <= set(groups["Cabezas"].fixture_ids)


def test_a_smoke_machine_swept_into_somebody_elses_scene(library):
    """A pump caught in an "all dimmers up" scene runs until the tank is dry."""
    workspace = _show()
    scene = _functions(workspace)["Blanco Total"]
    value = find_local(scene, "FixtureVal")
    # Fixture 17 is the AF-150: sweep its pump up with everything else.
    duplicate = value.makeelement(value.tag, {"ID": "17"})
    duplicate.text = "0,255"
    scene.append(duplicate)

    findings = [f for f in check_workspace(workspace, library) if f.rule == "humo"]
    assert any(f.function == "Blanco Total" for f in findings)


def test_a_fog_machine_fired_with_its_light_never_programmed(library):
    """2026-08-29, the vertical fog machines' manual: DMX priority kills the
    machine's internal colour program, so a show that fires the pump without
    ever writing dimmer + colour launches a column nobody lit. Strip every LED
    write to the machines - burst scene, colour bed, blackout - leaving only
    the pumps, and the checker must see the dark column."""
    from qlctool.capabilities_of import capabilities_of

    workspace = _show()
    machines = {
        c.fixture.fixture_id: set(fog_offsets(c))
        for c in capabilities_of(workspace.root, library)
        if c.is_lit_smoke
    }
    assert machines, "the split show should patch the vertical fog machines"
    for function in find_local(workspace.root, "Engine"):
        if localname(function) != "Function":
            continue
        for value in findall_local(function, "FixtureVal"):
            fixture_id = int(value.attrib["ID"])
            if fixture_id not in machines or not value.text:
                continue
            numbers = [int(n) for n in value.text.split(",")]
            kept = [
                (offset, level)
                for offset, level in zip(numbers[0::2], numbers[1::2])
                if offset in machines[fixture_id]
            ]
            if kept:
                value.text = ",".join(str(n) for pair in kept for n in pair)
            else:
                value.getparent().remove(value)

    findings = [f for f in check_workspace(workspace, library) if f.rule == "humo-luz"]
    assert findings, "the stripped show should read as a dark column"


def test_a_strobe_flashing_faster_than_four_hertz(library):
    """2026-08-27, Codex review of the highlight plan: `Strobo Rapido` had
    shipped alternating the whole rig between white and black every 50 ms -
    ten flashes a second, inside the photosensitive-epilepsy trigger band -
    and the checker said "ningun problema". Reproduced by putting the 50 ms
    steps back into the burst.
    """
    workspace = _show()
    chaser, _ = _burst_chaser(workspace, library, hold=50)

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "estrobo demasiado rapido"
    ]
    assert findings, "a 10 Hz whole-rig strobe went unnoticed"
    assert chaser.attrib["Name"] in {f.function for f in findings}


def test_a_strobe_that_loops_behind_a_button(library):
    """2026-08-27, same review: the console's STROBO was a Toggle over a
    looping chaser - one press and the rig flashed until somebody remembered
    which button had started it. A strobe hit has to be a bounded SingleShot
    burst that ends itself. Reproduced by putting the loop back.
    """
    workspace = _show()
    chaser, _ = _burst_chaser(workspace, library)
    find_local(chaser, "RunOrder").text = "Loop"

    findings = [f for f in check_workspace(workspace, library) if f.rule == "estrobo enganchado"]
    assert findings, "a latched looping strobe went unnoticed"
    assert chaser.attrib["Name"] in {f.function for f in findings}


def test_a_tap_that_flattens_every_programme(library):
    """2026-08-29, the owner on the speed dials: "nunca ha funcionado bien
    ... se vuelven todos los programas locos". A tap dial writes
    `time x multiplier` into each function it lists, so one shared multiplier
    makes the colour wheel, the prism and the dimmer pulse exactly as long as
    each other on the first tap. Reproduced by flattening the tempo dial's
    multipliers back to one value.
    """
    workspace = _show()
    dial = next(d for d in workspace.root.iter() if localname(d) == "SpeedDial" and _has_tap(d))
    for bound in findall_local(dial, "Function"):
        bound.set("Duration", "6")

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "tap que aplana los programas"
    ]
    assert findings, "a tap dial flattening every layer went unnoticed"


def _has_tap(dial):
    return any(localname(s) == "Input" and s.attrib.get("ID") == "1" for s in dial)


def test_a_beats_chaser_driving_millisecond_effects(library):
    """2026-08-29: "las cabezas van super rapido a 120bpm y no completan los
    giros". The movement chasers had been switched to Beats, so their 10-beat
    crossfade reached each EFX as the raw number 10000 - and an EFX subtracts
    its override fade from its own millisecond duration
    (`EFX::loopDuration`), turning a 16 s sweep into a 6 s one. Reproduced by
    putting Movimientos Washes back on Beats with its fade intact.

    Since 2026-09-02 every step of that chaser is a Collection of two EFX (the
    wash figures split on `efx_16bit`), and `Collection::write` hands the
    chaser's override fade straight to both - so the rule has to look through
    the Collection, and this test is what says it does.
    """
    workspace = _show()
    chaser = _functions(workspace)["Movimientos Washes"]
    ns = chaser.tag[: chaser.tag.index("}") + 1]
    tempo = chaser.makeelement(f"{ns}Tempo", {})
    tempo.text = "Beats"
    chaser.insert(0, tempo)

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "unidades de tempo cruzadas"
    ]
    assert findings, "a beats chaser re-timing its EFX went unnoticed"
    assert "Movimientos Washes" in {f.function for f in findings}


def test_a_collection_carrying_a_tempo_it_cannot_have(library):
    """2026-08-29, read out of the show Mac's own QLC+ log: "Unknown
    collection tag: Tempo". A Collection has no tempo - it starts its members
    and they keep their own - so a <Tempo> on one is a layer silently left on
    the stopwatch. Reproduced by giving Dimmer Chase the tag back.
    """
    workspace = _show()
    collection = _functions(workspace)["Dimmer Chase"]
    ns = collection.tag[: collection.tag.index("}") + 1]
    tempo = collection.makeelement(f"{ns}Tempo", {})
    tempo.text = "Beats"
    collection.insert(0, tempo)

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "tempo en una coleccion"
    ]
    assert findings, "a Collection carrying a Tempo went unnoticed"


def test_a_chaser_that_presses_the_room_state_buttons(library):
    """2026-08-29, the owner pressing the strobes: "strobo y strobo suave
    alternan entre parar y apagon y luego se para el show". The burst
    chasers stepped `Blanco Total` and `Todo Negro` - the room-state solo
    frame's own functions - and a qmlui Toggle button hears its function
    start no matter who started it, so each pulse pressed a state button by
    proxy and the solo frame killed AUTO. Reproduced by pointing the
    Strobo Rapido steps back at the state scenes instead of its twins.
    """
    workspace = _show()
    chaser, _ = _burst_chaser(workspace, library)
    functions = _functions(workspace)
    state_ids = {name: functions[name].attrib["ID"] for name in ("Blanco Total", "Todo Negro")}
    for index, step in enumerate(findall_local(chaser, "Step")):
        step.text = state_ids["Blanco Total" if index % 2 == 0 else "Todo Negro"]

    findings = [
        f
        for f in check_workspace(workspace, library)
        if f.rule == "estado pulsado por otra funcion"
    ]
    assert findings, "a chaser pressing the room-state buttons went unnoticed"
    assert chaser.attrib["Name"] in {f.function for f in findings}


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

    findings = [f for f in check_workspace(workspace, library) if f.rule == "flash sin estrobo"]
    assert findings, "a flash with its shutters parked open went unnoticed"
    assert "Flash 100%" in {f.function for f in findings}


def test_a_flash_that_strobes_at_a_stroll(library):
    """2026-08-29, the owner watching the PARs: "el flash para las par leds
    es entre 246-248 (strobo), como lo tenemos ahora es muy lento". The
    generator sat every fast flash at 0.85 of the slow-to-fast run - 217 on
    the CLB2.4's 1-255 strobe channel, where the hand-built show lived at
    246-250 - and no rule asked how fast a flash flashes. Reproduced by
    dropping every strobe value in the flash scenes back to 0.85 of its run.
    """
    workspace = _show()
    capabilities = {
        capability.fixture.fixture_id: capability
        for capability in capabilities_of(workspace.root, library)
    }
    functions = _functions(workspace)
    functions_by_id = {function.attrib["ID"]: function for function in functions.values()}
    flash_scene_ids = {
        target.attrib["ID"]
        for button in iter_local(workspace.root, "Button")
        if (action := find_local(button, "Action")) is not None
        and action.text == "Flash"
        and (target := find_local(button, "Function")) is not None
        and functions_by_id[target.attrib["ID"]].attrib.get("Type") == "Scene"
    }
    # The rule judges every Scene a hand can flash, including the library's
    # held colour looks. Lower every such strobe so no unrelated fast pick can
    # mask a room-wide slow flash.
    for function in functions.values():
        if function.attrib["ID"] not in flash_scene_ids:
            continue
        for value in findall_local(function, "FixtureVal"):
            capability = capabilities.get(int(value.attrib["ID"]))
            if capability is None or not value.text:
                continue
            numbers = [int(n) for n in value.text.split(",")]
            pairs = dict(zip(numbers[0::2], numbers[1::2], strict=True))
            for offset, strobing in strobe_capable_offsets(capability).items():
                if offset not in pairs:
                    continue
                if strobing is None:
                    pairs[offset] = round(0.85 * 255)
                else:
                    span = strobing.maximum - strobing.minimum
                    pairs[offset] = strobing.minimum + round(0.85 * span)
            value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))

    findings = [f for f in check_workspace(workspace, library) if f.rule == "flash lento"]
    assert findings, "a whole rig flashing at a stroll went unnoticed"
    assert any("CLB2.4" in fixture for f in findings for fixture in f.fixtures), (
        "the PAR heads the owner was watching are not in the finding"
    )


def test_a_slow_flash_that_crawls(library):
    """2026-08-29, same night as the fast flash: "el flash slow para los par
    es unos 200, no lo que esta ahora". FLASH_STROBE_SLOW at 0.45 put the
    CLB2.4's strobe at 115 of 1-255 where the owner's slow flash lives at
    ~200 (0.78) - a crawl nobody would call a flash. Reproduced by dropping
    the Flash 50% strobe values back to 0.45 of their run.
    """
    workspace = _show()
    capabilities = {
        capability.fixture.fixture_id: capability
        for capability in capabilities_of(workspace.root, library)
    }
    for value in findall_local(_functions(workspace)["Flash 50%"], "FixtureVal"):
        capability = capabilities.get(int(value.attrib["ID"]))
        if capability is None or not value.text:
            continue
        numbers = [int(n) for n in value.text.split(",")]
        pairs = dict(zip(numbers[0::2], numbers[1::2], strict=True))
        for offset, strobing in strobe_capable_offsets(capability).items():
            if offset not in pairs:
                continue
            if strobing is None:
                pairs[offset] = round(0.45 * 255)
            else:
                span = strobing.maximum - strobing.minimum
                pairs[offset] = strobing.minimum + round(0.45 * span)
        value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))

    findings = [f for f in check_workspace(workspace, library) if f.rule == "flash lento"]
    assert findings, "a slow flash crawling went unnoticed"
    assert "Flash 50%" in {f.function for f in findings}
    assert any("CLB2.4" in fixture for f in findings for fixture in f.fixtures), (
        "the PAR heads the owner was watching are not in the finding"
    )


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

    findings = [f for f in check_workspace(workspace, library) if f.rule == "estrobo incompleto"]
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
        f for f in check_workspace(workspace, library) if f.rule == "estrobo en manos del audio"
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

    findings = [f for f in check_workspace(workspace, library) if f.rule == "flash sin escena"]
    assert findings, "a Flash button over a Collection went unnoticed"


def test_a_shutter_opened_to_the_middle_of_its_open_range(library):
    """2026-08-29, live at the show: "si no tenemos el canal de strobe al 255
    no se muestra la luz". Every scene wrote 248 to the beams' shutter - dead
    centre of the range the manual calls "241-255 Open" - and the four 7R
    stayed black; at 255 they lit. A published range is a promise about its
    endpoint only. Reproduced by putting the middle value back.
    """
    workspace = _show()
    for function in _functions(workspace).values():
        if function.attrib.get("Type") != "Scene":
            continue
        for value in findall_local(function, "FixtureVal"):
            if int(value.attrib["ID"]) not in BEAMS or not value.text:
                continue
            numbers = [int(n) for n in value.text.split(",")]
            pairs = dict(zip(numbers[0::2], numbers[1::2], strict=True))
            if pairs.get(5) != 255:
                continue
            pairs[5] = 248
            value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "obturador a medio abrir"
    ]
    assert findings, "a shutter opened to a value the hardware ignores went unnoticed"


def test_a_wash_lit_by_a_scene_that_never_states_its_zoom(library):
    """2026-08-29: the two CromoWash did not make it to the show and two Mac Mah
    MAC WASH 1915Z came instead - the first fixtures in this rig with a zoom on
    DMX. Nothing here had ever written a zoom channel, so every colour scene lit
    them at whatever the last look left, which on a cold desk is 0: six degrees,
    a coin on the back wall from a fixture the plot calls a wash. Reproduced by
    taking the zoom back out of the scenes that light them.
    """
    workspace = _show()
    washes = {41, 42}
    zoom = 5
    for function in _functions(workspace).values():
        if function.attrib.get("Type") != "Scene":
            continue
        for value in findall_local(function, "FixtureVal"):
            if int(value.attrib["ID"]) not in washes or not value.text:
                continue
            numbers = [int(n) for n in value.text.split(",")]
            pairs = dict(zip(numbers[0::2], numbers[1::2], strict=True))
            if pairs.pop(zoom, None) is None:
                continue
            value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))

    findings = [f for f in check_workspace(workspace, library) if f.rule == "zoom sin declarar"]
    assert findings, "a wash lit with its zoom left at the narrow end went unnoticed"


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
    caps = {c.fixture.fixture_id: c for c in capabilities_of(workspace.root, library)}
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
            pairs.update(dict.fromkeys(offsets, 255))
            value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))

    findings = [f for f in check_workspace(workspace, library) if f.rule == "intensidad tapada"]
    assert findings, "a dimmer nobody can ever see went unnoticed"


def test_a_dimmer_effect_flattened_by_a_full_scene_beside_it(library):
    """2026-08-29, "modo locura empieza todo blanco y normal": `Momento
    Locura` carried `Intensidad Total` beside `Dimmer Chase`, and HTP made
    every dip the effect drew invisible - the room opened as a flat wall of
    light. `intensidad tapada` cannot see it because an EFX never states a
    value, but nothing an effect writes can exceed 255. Reproduced by putting
    `Intensidad Total` back where the dimmerless peak base now goes.
    """
    workspace = _show()
    functions = _functions(workspace)
    locura = functions["Momento Locura"]
    peak_id = functions["Intensidad Peak"].attrib["ID"]
    total_id = functions["Intensidad Total"].attrib["ID"]
    for step in findall_local(locura, "Step"):
        if step.text == peak_id:
            step.text = total_id

    findings = [f for f in check_workspace(workspace, library) if f.rule == "efx de dimmer tapado"]
    assert findings, "a dimmer effect nobody can ever see went unnoticed"


def test_a_flash_accent_on_a_wheel_no_state_puts_back(library):
    """2026-08-27: wheel channels are LTP - the last write stays. A Flash
    scene that moves the beams' colour wheel releases cleanly only if the
    state underneath also drives that wheel; otherwise the accent's position
    simply stays, and nobody can say which button left it there. Reproduced
    by taking the beams' white out of the `Luz Charla` COLOR hook.
    """
    workspace = _show()
    functions = _functions(workspace)
    charla = functions["Luz Charla"]
    white_id = functions["Color Beam - White"].attrib["ID"]
    for step in findall_local(charla, "Step"):
        if step.text == white_id:
            charla.remove(step)

    findings = [f for f in check_workspace(workspace, library) if f.rule == "acento sin dueño"]
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
        f
        for f in _functions(workspace).values()
        if f.attrib.get("Type") == "EFX" and f.attrib.get("Name", "").startswith("Wash ")
    )
    fixture = etree.SubElement(efx, f"{{{QLC_NS}}}Fixture")
    for tag, text in (
        ("ID", "20"),
        ("Head", "0"),
        ("Mode", "0"),
        ("Direction", "Forward"),
        ("StartOffset", "0"),
    ):
        child = etree.SubElement(fixture, f"{{{QLC_NS}}}{tag}")
        child.text = text

    findings = [
        f
        for f in check_workspace(workspace, library)
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
    widget = next(w for w in workspace.root.iter() if localname(w) == "AudioTriggers")
    for bar in findall_local(widget, "SpectrumBar"):
        widget.remove(bar)

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "disparador de audio vacio"
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
    _, strobe_button = _burst_chaser(workspace, library)
    widget = next(w for w in workspace.root.iter() if localname(w) == "AudioTriggers")
    bar = etree.SubElement(widget, f"{{{QLC_NS}}}SpectrumBar")
    bar.set("Name", "Graves")
    bar.set("Type", "3")
    bar.set("MinThreshold", "12")
    bar.set("MaxThreshold", "51")
    bar.set("Divisor", "1")
    bar.set("Index", "0")
    bar.set("WidgetID", strobe_button.attrib["ID"])

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "disparador de audio vacio"
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
            b
            for b in workspace.root.iter()
            if localname(b) == "Button"
            and (function := find_local(b, "Function")) is not None
            and function.attrib.get("ID") == function_id
        )

    widget = next(w for w in workspace.root.iter() if localname(w) == "AudioTriggers")

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
        f for f in check_workspace(workspace, library) if f.rule == "disparador de audio vacio"
    ]
    assert findings, "an audio bar pressing a room-state button went unnoticed"

    bind(button_for("Flash 100%").attrib["ID"])
    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "disparador de audio vacio"
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
    widget = next(w for w in workspace.root.iter() if localname(w) == "AudioTriggers")
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
        f for f in check_workspace(workspace, library) if f.rule == "disparador de audio vacio"
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

    findings = [f for f in check_workspace(workspace, library) if f.rule == "estrobo pegado"]
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
    step_names = {f.attrib.get("Name") for f in functions.values() if f.attrib.get("ID") in steps}
    assert step_names == {"Ciclo Paneles", "Paneles Manual"}

    rig_scenes = [
        f
        for name, f in functions.items()
        if name
        and name.startswith(("Rig ", "Cabezas "))
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

    findings = [f for f in check_workspace(workspace, library) if f.rule == "programa interno"]
    assert findings, "colour with no standing mode owner went unnoticed"
    assert any("WX-60WPS" in fixture for f in findings for fixture in f.fixtures)


def test_a_console_bound_to_a_control_the_pad_cannot_send(library):
    """2026-08-29: eight buttons on the manual page listened to nothing.

    They were bound against SHIFT, on the notes the pad's factory bank would
    have sent 48 semitones up. A capture that night, owner pressing, showed
    SHIFT puts nothing on the wire at all - it selects the functions
    silkscreened on the pads (SWING, LATCH, SYNC), which never leave the
    device - so those bindings had never fired and looked identical to the
    ones that had. The manual layer moved to the pad's second bank, which
    PAD BANK does send (PAD1 answered note 52 instead of 36).

    Put a binding back on a channel no control sends and the rule must bite.
    """
    workspace = _show()
    console = find_local(workspace.root, "VirtualConsole")
    moved = None
    for button in console.iter():
        if localname(button) != "Button":
            continue
        source = find_local(button, "Input")
        if source is None or "Channel" not in source.attrib:
            continue
        # Note 100: a bank the show never selects, so nothing can press it.
        source.set("Channel", str(36992 + 100))
        moved = button.attrib.get("Caption")
        break
    assert moved, "the shipped console carries no MIDI binding to move"

    findings = check_workspace(workspace, library)
    unsendable = [f for f in findings if f.rule == "binding a un control que el pad no manda"]
    assert unsendable, "a binding on a note the pad cannot send went unnoticed"
    assert any(f.function == moved for f in unsendable)


def test_a_console_full_of_bindings_with_nothing_listening(library):
    """2026-08-29: `Vibra-split.qxw` shipped with no MIDI input patch.

    Every `<Input>` in that file was inert - QLC+ opened the show with no input
    plugin on the universe, so the pad did nothing until somebody built the
    patch by hand in the Inputs/Outputs tab. (The other two shows carried the
    owner's own patch, which is why regenerating must preserve it rather than
    write one of its own - see `test_input_profile.py`.) Take the patch away
    again and the rule must say the surface is dead.
    """
    workspace = _show()
    universe = find_local(
        find_local(find_local(workspace.root, "Engine"), "InputOutputMap"), "Universe"
    )
    patch = find_local(universe, "Input")
    assert patch is not None, "the shipped show no longer patches its MIDI input"
    universe.remove(patch)

    findings = check_workspace(workspace, library)
    assert [f for f in findings if f.rule == "consola con bindings y sin entrada MIDI"], (
        "a console whose bindings reach no input plugin went unnoticed"
    )


def test_a_rig_colour_that_spins_the_beams_wheel_instead_of_naming_one(library):
    """2026-08-29: "las 7R no se abren del todo, están como una media luna".

    Live under AUTO, nothing else pressed. Nothing was closed: two of the
    twenty steps of the colour clock - `Rig Multicolor 1` and `Rig Multicolor
    2` - put the beams' colour wheel at 186, inside its rotation range and near
    the slow end. A turning wheel spends its time between detents, and a
    2-degree beam looking through a split wheel shows half of one colour and
    half of the next. Put the scroll value back and the rule must bite.
    """
    workspace = _show()
    functions = _functions(workspace)
    scene = functions["Rig Multicolor 1"]
    wheel = {
        capability.fixture.fixture_id: capability.wheel_for_role(roles.COLOR_MACRO)[0]
        for capability in capabilities_of(workspace.root, library)
        if capability.fixture.fixture_id in BEAMS
    }
    for value in findall_local(scene, "FixtureVal"):
        fixture_id = int(value.attrib["ID"])
        if fixture_id not in wheel:
            continue
        value.text = f"{wheel[fixture_id]},186"

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "rueda de color girando"
    ]
    assert findings, "a rig colour spinning the beams' wheel went unnoticed"
    assert "Rig Multicolor 1" in {f.function for f in findings}
    assert all("BEAM" in fixture for f in findings for fixture in f.fixtures)


def test_a_level_of_the_cycle_that_parks_half_the_movers(library):
    """2026-08-29: "las 7R ... no se mueven", again with only AUTO pressed.

    `Nivel Ambiente` is the first and longest step of `Ciclo Energia`: its
    `Movimientos Suaves` Collection starts both slow chasers. Swap the beams'
    slow rotation back for a static fan and the rule must bite.
    """
    workspace = Workspace.load(REPO / "QLC+ Setups" / "DeluxeEventos2.qxw")
    build_canonical_show(workspace, library, with_layout=False)
    functions = _functions(workspace)
    by_name = {
        name: int(function.attrib["ID"])
        for name, function in functions.items()
        if function.attrib.get("ID")
    }
    level = functions["Movimientos Suaves"]
    slow_beams = str(by_name["Suaves Beams"])
    fan = str(by_name["Beams Abanico"])
    swapped = False
    for step in findall_local(level, "Step"):
        if (step.text or "").strip() == slow_beams:
            step.text = fan
            swapped = True
    assert swapped, "`Movimientos Suaves` no longer moves the beams at all"

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "cabezas paradas en el ciclo"
    ]
    assert findings, "a cycle level parking the beams went unnoticed"
    assert "Nivel Ambiente" in {f.function for f in findings}
    assert all("BEAM" in fixture for f in findings for fixture in f.fixtures)


def test_a_split_movement_is_not_a_block_that_parks_the_beams(library):
    """2026-09-02: the wash figures became pairs of EFX, and the rule bit.

    The Mini Led Moving Head's channels 9-16 were settled off three agreeing
    OEM charts, which put its fine channels at 14 and 15 - not beside the
    coarse ones - so every wash figure is now a 16-bit EFX and an 8-bit EFX
    under one Collection (`efx_16bit`). As a step of the washes' chaser that
    Collection moves the washes and not the beams, exactly as the single EFX
    did, and the beams' chaser beside it moves the beams. The rule must read
    it as one movement, not as a block of the cycle parking four 7R - while a
    block that mixes a static scene into the step still bites (the test
    above).
    """
    workspace = _show()
    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "cabezas paradas en el ciclo"
    ]
    assert not findings, [f.function for f in findings]
    functions = _functions(workspace)
    pairs = [
        name
        for name, function in functions.items()
        if function.attrib.get("Type") == "Collection" and (name or "").startswith("Wash ")
    ]
    assert pairs, "the wash figures are no longer split into EFX pairs"


def test_a_beam_figure_centred_on_mid_travel(library):
    """2026-08-29: "está todo el rato haciendo un circulo pequeño en el suelo".

    Every movement EFX carried QLC+'s own axis default - tilt offset 127, the
    raw middle of the channel - because nothing had ever overridden it. Mid
    travel is not a place: on the 7R it is the floor, on the washes the wall
    behind the stage. Put the default back on a beam figure and the rule must
    bite.
    """
    workspace = _show()
    functions = _functions(workspace)
    efx = functions["Beam Suave Circulo"]
    axis = next(a for a in findall_local(efx, "Axis") if a.attrib.get("Name") == "Y")
    offset = find_local(axis, "Offset")
    assert offset.text != "127", "the beams' figure is aimed at mid travel again"
    offset.text = "127"

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "movimiento sin apuntar"
    ]
    assert findings, "a beam figure centred on mid travel went unnoticed"
    assert "Beam Suave Circulo" in {f.function for f in findings}
    assert all("BEAM" in fixture for f in findings for fixture in f.fixtures)


def test_a_fraction_written_to_a_blade_dimmer(library):
    """2026-08-29, the owner reading the desk during the show: "el canal 7 de
    cada 7R está a la mitad en vez de abierto del todo".

    Channel 7 is the BEAM 230W 7R's dimmer, and on a 7R that is a mechanical
    blade, not a fader. `Intensidad Ambiente` wrote 110 to every dimmer in the
    rig and the quiet level held it for four minutes, so the blade sat half
    across the lens: "están como una media luna". Put the fraction back and the
    rule must bite.
    """
    workspace = _show()
    functions = _functions(workspace)
    scene = functions["Intensidad Ambiente"]
    dimmers = {
        capability.fixture.fixture_id: capability.offsets_for_role(roles.DIMMER)
        for capability in capabilities_of(workspace.root, library)
        if capability.fixture.fixture_id in BEAMS
    }
    for value in findall_local(scene, "FixtureVal"):
        fixture_id = int(value.attrib["ID"])
        if fixture_id not in dimmers:
            continue
        numbers = [int(n) for n in (value.text or "").split(",") if n != ""]
        pairs = dict(zip(numbers[0::2], numbers[1::2], strict=True))
        for offset in dimmers[fixture_id]:
            pairs[offset] = 110
        value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))

    findings = [f for f in check_workspace(workspace, library) if f.rule == "dimmer a medias"]
    assert findings, "a fraction on a blade dimmer went unnoticed"
    assert "Intensidad Ambiente" in {f.function for f in findings}
    assert all("BEAM" in fixture for f in findings for fixture in f.fixtures)


def test_a_dimmer_efx_sweeping_a_blade_dimmer(library):
    """The same fault in motion: an EFX in Dimmer mode over the blade sweeps it,
    so most of every pass is a half-moon rather than a dip (2026-08-29).
    """
    workspace = _show()
    efx = _functions(workspace)["Dimmer Chase CromoWash100"]
    member = findall_local(efx, "Fixture")[0]
    find_local(member, "ID").text = str(BEAMS[0])

    findings = [f for f in check_workspace(workspace, library) if f.rule == "dimmer a medias"]
    assert findings, "a dimmer EFX sweeping a blade went unnoticed"
    assert any("BEAM" in fixture for f in findings for fixture in f.fixtures)


def test_a_beam_figure_that_leaves_the_audience(library):
    """2026-08-29: the aim was guessed twice and was wrong twice - the beams
    drew a circle on the floor, then pointed at the wall behind.

    It ended with the owner putting BEAM 230W 7R #1 on the desk and sending the
    corners of where the people are: "eso son los rangos del publico, todo lo
    fuera de eso ya apunta a fuera". With the window written down the question
    is arithmetic. Grow a figure past it and the rule must bite.
    """
    workspace = _show()
    efx = _functions(workspace)["Beam Circulo"]
    height = find_local(efx, "Height")
    inside = int(height.text)
    assert BEAM_WINDOW.holds(
        int(
            find_local(
                next(a for a in findall_local(efx, "Axis") if a.attrib.get("Name") == "Y"), "Offset"
            ).text
        ),
        inside,
        "tilt",
    ), "the shipped beam figure already leaves the audience window"
    height.text = str(inside + 40)

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "figura fuera del publico"
    ]
    assert findings, "a beam figure sweeping out of the room went unnoticed"
    assert "Beam Circulo" in {f.function for f in findings}
    assert all("BEAM" in fixture for f in findings for fixture in f.fixtures)


def test_a_held_pump_on_a_channel_qlcplus_never_resets(library):
    """The rest of the same night. Holding the button did not stop it either:
    "le doy y no para de echar todo el rato".

    QLC+ rebuilds the universe from the running faders every cycle but only
    resets the **Intensity** group first (`Universe::processFaders` ->
    `zeroIntensityChannels`); every other group keeps its last value. The Fog
    channel was declared in Effect, so releasing the flash removed the flash's
    fader and changed nothing. Put the pump back outside the reset group and
    the rule must bite.
    """
    from dataclasses import replace

    workspace = _show()
    broken = FixtureLibrary.load()
    definition = broken.get("Generic", "LED Spray Fog")
    assert definition is not None, "the vertical fog machines left the library"
    pump = definition.channels["Fog"]
    assert pump.group.lower() == "intensity", "the pump left the reset group"
    definition.channels["Fog"] = replace(pump, group="Effect")

    findings = [f for f in check_workspace(workspace, broken) if f.rule == "humo pegado"]
    assert findings, "a held pump QLC+ never resets went unnoticed"
    assert any("Humo" in fixture for f in findings for fixture in f.fixtures)


def test_a_head_nothing_takes_off_its_own_programme(library):
    """2026-08-30, the two MAC WASH 1915Z on their first night: "se quedaban
    mirando para abajo y hacian cosas raras como una especie de cambios de
    colores muy rapidos".

    The movement was aimed at the measured audience window and the colour was
    a wheel stepping every eight beats, so what the room saw was not the show
    at all: the fixture was running itself. Its `Function Mode` channel is one
    blanket 000-255 range - nothing for `rule_internal_program` to match on -
    and no function in the show wrote it, so it kept whatever the last
    controller left there. Take the parked value back out and the rule must
    bite.
    """
    workspace = _show()
    capabilities = {
        capability.fixture.fixture_id: capability
        for capability in capabilities_of(workspace.root, library)
    }
    victims = {
        fixture_id: capability.offsets_for_role(roles.EFFECT)
        for fixture_id, capability in capabilities.items()
        if capability.has_role(roles.EFFECT)
        and capability.has_role(roles.PAN)
        and capability.has_role(roles.RED)
    }
    assert victims, "no RGB moving head in the show carries a mode channel"

    stripped = 0
    for function in find_local(workspace.root, "Engine"):
        for element in findall_local(function, "FixtureVal"):
            offsets = victims.get(int(element.attrib.get("ID", -1)))
            if not offsets or not element.text:
                continue
            numbers = [int(n) for n in element.text.split(",") if n != ""]
            kept = [
                (channel, value)
                for channel, value in zip(numbers[::2], numbers[1::2], strict=True)
                if channel not in offsets
            ]
            if len(kept) * 2 != len(numbers):
                stripped += 1
            element.text = ",".join(str(n) for pair in kept for n in pair)
    assert stripped, "the show never parked the mode channel to begin with"

    findings = [f for f in check_workspace(workspace, library) if f.rule == "modo sin dueño"]
    assert findings, "a head left running its own programme went unnoticed"
    assert any(
        capabilities[fixture_id].fixture.name in f.fixtures
        for f in findings
        for fixture_id in victims
    )


def test_a_smoke_column_a_latched_button_can_fire(library):
    """2026-08-30: "el humo vertical nunca debe dispararse solo" (owner).

    The four vertical machines fire a lit column and empty a tank doing it,
    which is why their button is a Flash and their pump is in the group QLC+
    resets every cycle. Neither helps if the same scene is reachable from a
    button that latches - AUTO, a level, a Toggle - so the wiring is the rule:
    turn the column's own button into a Toggle and it must bite.
    """
    workspace = _show()
    console = find_local(workspace.root, "VirtualConsole")
    switched = 0
    for button in iter_local(console, "Button"):
        if "HUMO VERT ·" not in (button.attrib.get("Caption") or ""):
            continue
        action = find_local(button, "Action")
        assert action is not None and action.text == "Flash"
        action.text = "Toggle"
        switched += 1
    assert switched, "the console lost its vertical smoke button"

    findings = [f for f in check_workspace(workspace, library) if f.rule == "columna automatica"]
    assert findings, "a latched smoke column went unnoticed"
    assert any("Humo Vertical" in fixture for f in findings for fixture in f.fixtures)


def test_one_wheel_step_cannot_switch_the_strobe_off_for_all_of_them(library):
    """2026-08-28, from the Codex review of `estrobo pegado`: the rule merged
    the reach of everything hanging off a state, so a strobe-off written under
    one alternative read as though it were written under all of them.

    A chaser's steps are not concurrent - they are different rooms, one at a
    time. Reproduced by leaving the panels' strobe-off in a single step of
    `Ciclo Paneles` and taking it out of everywhere else: AUTO's merged reach
    still finds a strobe-off, which is what made the old rule pass, while the
    room spends the other 41 steps latched.
    """
    workspace = _show()
    panels = {24, 25, 27, 28}
    # The two states that are a Scene themselves keep theirs, so that under the
    # old merged reach every lit state still had an owner and the rule was
    # silent - which is what this test is here to break.
    kept = {"Paneles - Effect 1", "Blanco Total", "Intensidad Charla Pixeles"}
    stripped = 0
    for name, function in _functions(workspace).items():
        if function.attrib.get("Type") != "Scene" or name in kept:
            continue
        for value in findall_local(function, "FixtureVal"):
            if int(value.attrib["ID"]) not in panels or not value.text:
                continue
            numbers = [int(n) for n in value.text.split(",")]
            pairs = dict(zip(numbers[0::2], numbers[1::2], strict=True))
            if pairs.get(4) == 0:  # channel 5 is the strobe; leave the
                pairs.pop(4)  # flash scenes' own strobing value alone
                stripped += 1
            value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))
    assert stripped, "the repro changed nothing; the scene shape moved"

    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    groups = group_fixtures(workspace.root)
    states = room_states(workspace.root, graph, groups)
    merged = {state_id: reach(graph, groups, state_id).get(24, {}) for state_id in states}
    assert all(4 in written for written in merged.values() if lit(written.get(0, 0))), (
        "the old merged reach would have caught this on its own; repro too broad"
    )

    findings = [f for f in check_workspace(workspace, library) if f.rule == "estrobo pegado"]

    assert findings, (
        "a strobe-off surviving in one wheel step masked every step that lost "
        "it - the union is back"
    )
    assert any("WX-60WPS" in fixture for f in findings for fixture in f.fixtures)


def test_a_fixture_with_three_rings_and_one_head_is_caught(tmp_path):
    """2026-08-31: the two MAC WASH 1915Z were about to be put in a fixture
    group so they would finally get a colour bank and a matrix. Their 23-channel
    mode has `Red/Green/Blue ring 1..3` and declared no `<Head>` at all.

    QLC+ does not read that as "no heads": it builds one head holding every
    channel, and that head keeps only the last channel of each colour. A matrix
    would have painted the outer ring and left the other two holding whatever
    was written last - the panels' bug, on part of a fixture. Reproduced by
    taking the heads back out of the definition.
    """
    for qxf in (REPO / "QLC+ Fixtures").glob("*.qxf"):
        text = qxf.read_text(encoding="utf-8")
        if qxf.name.startswith("Mac-Mah-MAC-WASH"):
            text = re.sub(r" *<Head>.*?</Head>\n", "", text, flags=re.S)
            assert "<Head>" not in text
        (tmp_path / qxf.name).write_text(text, encoding="utf-8")
    headless = FixtureLibrary.load(tmp_path)

    from lxml import etree

    from qlctool.constants import QLC_NS

    workspace = _show()
    group = next(
        element
        for element in workspace.root.iter()
        if localname(element) == "FixtureGroup"
        and (find_local(element, "Name").text or "") == "Cabezas"
    )
    size = find_local(group, "Size")
    size.set("X", str(int(size.attrib["X"]) + 2))
    for cell, fixture_id in enumerate((41, 42)):
        head = etree.SubElement(group, f"{{{QLC_NS}}}Head")
        head.set("X", str(int(size.attrib["X"]) - 2 + cell))
        head.set("Y", "0")
        head.set("Fixture", str(fixture_id))
        head.text = "0"

    findings = [f for f in check_workspace(workspace, headless) if f.rule == "cabezas sin declarar"]

    assert findings, "a fixture offering a matrix one of its three rings went unnoticed"
    assert any("MAC WASH" in fixture for f in findings for fixture in f.fixtures)


def test_the_shipped_definitions_declare_a_head_per_colour_set(library):
    """The other half of the rule: every fixture the show patches must already
    satisfy it, or the rule is only true of the one file it was written for."""
    for name in SHOWS:
        workspace = _show(name)
        graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
        assert not check_undeclared_heads(graph, workspace.root)


def test_three_empty_head_blocks_do_not_satisfy_the_rule(tmp_path):
    """Found in review, 2026-08-31: counting `<Head>` elements is not the same
    as counting heads that hold a colour. Three blocks listing the pan and tilt
    channels satisfy a count and leave the matrix exactly as broken."""
    for qxf in (REPO / "QLC+ Fixtures").glob("*.qxf"):
        text = qxf.read_text(encoding="utf-8")
        if qxf.name.startswith("Mac-Mah-MAC-WASH"):
            text = re.sub(
                r"( *<Head>\n)(?: *<Channel>\d+</Channel>\n)+",
                r"\1   <Channel>0</Channel>\n   <Channel>2</Channel>\n",
                text,
            )
            assert text.count("<Head>") == 3
        (tmp_path / qxf.name).write_text(text, encoding="utf-8")
    colourless = FixtureLibrary.load(tmp_path)

    workspace = _show()
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, colourless))

    findings = check_undeclared_heads(graph, workspace.root)

    assert findings, "three heads holding no colour passed the head count"
    assert any("MAC WASH" in fixture for f in findings for fixture in f.fixtures)


# --- the cross-audit of 2026-09-02: two simulators against forty-four rules ---


def _pairs_of(value):
    numbers = [int(n) for n in (value.text or "").split(",") if n != ""]
    return dict(zip(numbers[0::2], numbers[1::2], strict=True))


def _write_pairs(value, pairs):
    value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))


def _button_of(workspace, function_id):
    return next(
        b
        for b in workspace.root.iter()
        if localname(b) == "Button"
        and (function := find_local(b, "Function")) is not None
        and function.attrib.get("ID") == str(function_id)
    )


def _family_frame(workspace, function_names, *, caption="TEST FAMILY", solo=True, nested=False):
    """Add a small test frame with Toggle buttons for the named functions."""
    from qlctool.vc.button import build_button
    from qlctool.vc.frame import build_frame
    from qlctool.vc.widget_ids import next_widget_id

    root = find_local(find_local(workspace.root, "VirtualConsole"), "Frame")
    frame = build_frame(
        root,
        next_widget_id(workspace.root),
        caption,
        x=0,
        y=0,
        width=700,
        height=100,
        solo=solo,
    )
    button_parent = frame
    if nested:
        button_parent = build_frame(
            frame,
            next_widget_id(workspace.root),
            "TEST NESTED FAMILY",
            x=0,
            y=0,
            width=680,
            height=70,
            pages=2,
        )
    functions = _functions(workspace)
    for index, name in enumerate(function_names):
        build_button(
            button_parent,
            next_widget_id(workspace.root),
            name,
            int(functions[name].attrib["ID"]),
            x=index * 110,
            y=30,
            width=105,
            height=50,
        )
    return button_parent


def _wrapper_button(workspace, frame, source_name, wrapper_name):
    """Add a one-member Collection wrapper and its Toggle button."""
    from qlctool.functions.collection import build_collection
    from qlctool.ids import next_function_id
    from qlctool.vc.button import build_button
    from qlctool.vc.widget_ids import next_widget_id

    source_id = int(_functions(workspace)[source_name].attrib["ID"])
    wrapper_id = next_function_id(workspace.root)
    workspace.add_function(build_collection(wrapper_id, wrapper_name, [source_id]))
    build_button(
        frame,
        next_widget_id(workspace.root),
        wrapper_name,
        wrapper_id,
        x=550,
        y=30,
        width=105,
        height=50,
    )
    return wrapper_id


def test_a_family_pick_that_is_reachable_from_a_room_state(library):
    """2026-09-02, play-page design: a wheel step used as its own pick
    reports that state-driven start to the SoloFrame and releases the hook.
    The pick must target a one-member wrapper instead.
    """
    workspace = _show()
    _family_frame(
        workspace,
        ("Rueda Colores", "Rueda Mezcla", "Luz Charla", "Rig Rojo + Pixeles"),
    )

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert any(
        f.function == "Rig Rojo + Pixeles" and "es un pick" in f.message for f in findings
    ), "a state-reachable family pick went unnoticed"


def test_a_family_frame_missing_a_state_owner(library):
    """2026-09-02, play-page design: Momento Charla colours the rig through
    Luz Charla, so the COLOR frame needs that hook as well as the AUTO wheel.
    """
    workspace = _show()
    _family_frame(workspace, ("Rueda Colores", "Rueda Mezcla"))

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert any(
        f.function == "Luz Charla" and "no tiene su Toggle" in f.message for f in findings
    ), "a family frame missing Luz Charla's hook went unnoticed"


def test_a_pick_cannot_dark_a_moment_by_stopping_its_hook(library):
    """2026-09-02: pressing a COLOR pick stops its hook. If that hook alone
    opens Momento Charla's dimmers, the pick paints a black room.
    """
    from lxml import etree

    from qlctool.constants import QLC_NS

    workspace = Workspace.load(REPO / "QLC+ Setups" / "DeluxeEventos2.qxw")
    build_canonical_show(workspace, library)
    functions = _functions(workspace)
    charla = functions["Luz Charla"]
    moment = functions["Momento Charla"]
    intensity_id = functions["Intensidad Total"].attrib["ID"]

    for step in findall_local(moment, "Step"):
        if step.text == intensity_id:
            moment.remove(step)
    if intensity_id not in {step.text for step in findall_local(charla, "Step")}:
        etree.SubElement(charla, f"{{{QLC_NS}}}Step").text = intensity_id

    findings = [f for f in check_workspace(workspace, library) if f.rule == "pick que apaga"]
    assert any(f.function == "Momento Charla" for f in findings), (
        "a pick darkening Momento Charla by stopping Luz Charla went unnoticed"
    )


def test_a_pick_only_colour_cannot_leave_a_dimmer_unwritten(library):
    """2026-09-02: a latched JUGAR pick can be the only colour after it stops
    Momento Charla's hook, so it still needs a dimmer writer.
    """
    workspace = _show("Vibra.qxw")
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    panel = next(
        capability
        for capability in graph.capabilities.values()
        if "WX-60WPS" in capability.fixture.name
    )
    functions = _functions(workspace)
    moment = functions["Momento Charla"]
    charla_id = functions["Luz Charla"].attrib["ID"]
    for step in findall_local(moment, "Step"):
        if step.text != charla_id:
            moment.remove(step)

    findings = [f for f in check_workspace(workspace, library) if f.rule == "pick que apaga"]

    assert any(
        f.function == "Momento Charla" and panel.fixture.name in f.fixtures for f in findings
    ), "a pick-only colour with no dimmer writer went unnoticed"


def test_pick_darkens_checks_a_state_with_no_active_hook(library):
    """2026-09-02: Todo Negro reaches none of the COLOR frame's hooks, but a
    latched colour pick still runs beside it and needs an open shutter owner.
    """
    workspace = _show("Vibra-split.qxw")
    capabilities = capabilities_of(workspace.root, library)
    graph = build_show_graph(workspace.root, capabilities)
    groups = group_fixtures(workspace.root)
    functions = _functions(workspace)
    black_id = int(functions["Todo Negro"].attrib["ID"])
    charla_id = int(functions["Momento Charla"].attrib["ID"])
    pick_name = "Jugar · Rig Rojo + Pixeles"

    hook_ids = {int(functions[name].attrib["ID"]) for name in ("Rueda Colores", "Luz Charla")}
    assert not hook_ids & graph.descendants(black_id)

    min_washes = {
        capability.fixture.fixture_id: capability
        for capability in capabilities
        if capability.fixture.model == "MiN Wash"
    }
    assert len(min_washes) == 2
    for value in findall_local(functions["Todo Negro"], "FixtureVal"):
        fixture_id = int(value.attrib["ID"])
        capability = min_washes.get(fixture_id)
        if capability is None:
            continue
        pairs = _pairs_of(value)
        for shutter in capability.offsets_for_role(roles.STROBE):
            pairs.pop(shutter, None)
        _write_pairs(value, pairs)

    graph = build_show_graph(workspace.root, capabilities)
    findings = check_pick_darkens(
        graph,
        groups,
        workspace.root,
        {black_id, charla_id},
    )

    assert any(
        finding.function == "Todo Negro"
        and f"«{pick_name}»" in finding.message
        and set(finding.fixtures) == {"MiN Wash #1", "MiN Wash #2"}
        for finding in findings
    ), "the no-active-hook state/pick pair was skipped"


def test_pick_darkens_reuses_instant_root_states(library):
    """One room state is evaluated beside every latched pick; its immutable
    graph states must not be rebuilt once per fixture channel and pick.
    """
    import cProfile

    workspace = _show("Vibra-split.qxw")
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    groups = group_fixtures(workspace.root)
    charla_id = int(_functions(workspace)["Momento Charla"].attrib["ID"])
    profiler = cProfile.Profile()

    profiler.runcall(
        check_pick_darkens,
        graph,
        groups,
        workspace.root,
        {charla_id},
    )

    node_state_calls = sum(
        entry.callcount
        for entry in profiler.getstats()
        if getattr(entry.code, "co_name", "") == "_node_states"
    )
    assert node_state_calls < 40_000, (
        f"one state rebuilt {node_state_calls} instant graph nodes across its picks"
    )


@pytest.mark.parametrize("name", SHOWS)
def test_every_regenerated_show_has_no_dark_state_pick_pair(name, library):
    """The generator fixes the state/pick behavior without touching shipped
    workspaces in this focused fix wave.
    """
    workspace = _show(name)
    build_canonical_show(workspace, library, with_layout=False)
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    groups = group_fixtures(workspace.root)
    states = room_states(workspace.root, graph, groups)

    findings = check_pick_darkens(graph, groups, workspace.root, states)

    assert not findings, "\n".join(str(finding) for finding in findings)


def test_a_higher_pick_shutter_value_can_close_a_concurrent_state(library):
    """2026-09-02: HTP chooses the higher shutter value, not whichever
    concurrent root the predicate happened to visit first.
    """
    from lxml import etree

    from qlctool.constants import QLC_NS
    from qlctool.definition import Capability
    from qlctool.functions.scene import build_scene
    from qlctool.ids import next_function_id

    workspace = _show("Vibra.qxw")
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    groups = group_fixtures(workspace.root)
    functions = _functions(workspace)
    mac = graph.capabilities[33]
    shutter = mac.offsets_for_role(roles.STROBE)[0]
    mac.capabilities_by_offset[shutter] = (
        Capability(0, 9, "Open", "ShutterOpen"),
        Capability(10, 255, "Closed", "ShutterClose"),
    )
    open_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(open_id, "TEST low shutter", {33: [(shutter, 0)]}))
    etree.SubElement(functions["Momento Charla"], f"{{{QLC_NS}}}Step").text = str(open_id)
    closed_id = next_function_id(workspace.root)
    workspace.add_function(
        build_scene(closed_id, "TEST high shutter pick", {33: [(shutter, 255), (8, 255)]})
    )
    _family_frame(workspace, ("Luz Charla", "TEST high shutter pick"))
    graph = build_show_graph(workspace.root, list(graph.capabilities.values()))
    states = room_states(workspace.root, graph, groups)

    findings = check_pick_darkens(graph, groups, workspace.root, states)

    assert any(
        f.function == "Momento Charla" and mac.fixture.name in f.fixtures for f in findings
    ), "a higher closed shutter value did not win its concurrent open value"


def test_pick_darkens_checks_each_pick_and_ignores_flash_buttons(library):
    """2026-09-02: every Toggle pick is checked independently, while a Flash
    does not latch and must not be treated as a SoloFrame replacement.
    """
    from lxml import etree

    from qlctool.constants import QLC_NS

    workspace = _show("Vibra.qxw")
    functions = _functions(workspace)
    charla_id = functions["Luz Charla"].attrib["ID"]
    for state_name in ("Momento Charla", "Momento Tranquilo"):
        state = functions[state_name]
        for step in findall_local(state, "Step"):
            state.remove(step)
        step = etree.SubElement(state, f"{{{QLC_NS}}}Step")
        step.text = charla_id
    first_pick = "Jugar · Rig Rojo + Pixeles"
    second_pick = "Jugar · Rig Verde + Pixeles"
    first_button = _button_of(workspace, functions[first_pick].attrib["ID"])
    action = find_local(first_button, "Action")
    action.text = "Flash"
    action.attrib.clear()

    findings = [f for f in check_workspace(workspace, library) if f.rule == "pick que apaga"]

    assert not any(f"«{first_pick}»" in f.message for f in findings)
    assert {
        "Momento Charla",
        "Momento Tranquilo",
    } <= {finding.function for finding in findings if f"«{second_pick}»" in finding.message}


def test_a_family_hook_reachable_from_another_frame_button(library):
    """2026-09-02, play-page design: a wrapper over a hook in the same
    SoloFrame starts that hook and immediately makes the frame stop it.
    """
    workspace = _show()
    frame = _family_frame(workspace, ("Rueda Colores", "Rueda Mezcla", "Luz Charla"))
    _wrapper_button(workspace, frame, "Rueda Colores", "TEST wrapped colour hook")

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert any(
        f.function == "TEST wrapped colour hook" and "arranca el hook" in f.message
        for f in findings
    ), "a family hook started by another frame button went unnoticed"


def test_a_complete_family_frame_with_wrapped_picks_is_silent(library):
    """2026-09-02, play-page design: complete hooks and an isolated wrapper
    let a pick replace AUTO without a state-driven start releasing it.
    """
    workspace = Workspace.load(REPO / "QLC+ Setups" / "DeluxeEventos2.qxw")
    build_canonical_show(workspace, library)
    frame = _family_frame(
        workspace,
        (
            "Rueda Colores",
            "Rueda Mezcla",
            "Luz Charla",
            "Ciclo Paneles Mixto",
            "Paneles Charla",
        ),
    )
    _wrapper_button(workspace, frame, "Rig Rojo + Pixeles", "TEST wrapped red pick")

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert not findings, "a correctly owned family frame should be silent"


def test_a_nested_family_frame_still_requires_every_state_owner(library):
    """2026-09-02, play-page design: a nested multipage frame still belongs
    to its nearest SoloFrame, so the missing Charla hook cannot hide inside it.
    """
    workspace = _show()
    _family_frame(workspace, ("Rueda Colores", "Rueda Mezcla"), nested=True)

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert any(f.function == "Luz Charla" for f in findings)


def test_a_nested_family_frame_exempts_its_wrapper_pick(library):
    """2026-09-02, play-page design: an inner plain/multipage frame inherits
    the complete outer SoloFrame and therefore keeps its wrapper layer exempt.
    """
    workspace = Workspace.load(REPO / "QLC+ Setups" / "DeluxeEventos2.qxw")
    build_canonical_show(workspace, library)
    frame = _family_frame(
        workspace,
        (
            "Rueda Colores",
            "Rueda Mezcla",
            "Luz Charla",
            "Ciclo Paneles Mixto",
            "Paneles Charla",
        ),
        nested=True,
    )
    _wrapper_button(workspace, frame, "Rig Rojo + Pixeles", "TEST nested red pick")

    findings = check_workspace(workspace, library)
    assert not [f for f in findings if f.rule == "familia con dueño"]
    assert not [
        f
        for f in findings
        if f.rule == "capa que se suma al estado" and f.function == "TEST nested red pick"
    ]


def test_a_zero_panel_effect_is_still_pixel_mode_ownership(library):
    """2026-09-02: mode zero is an intentional write, not an unowned channel."""
    from qlctool.checks.family_frames import _function_families

    workspace = Workspace.load(REPO / "QLC+ Setups" / "DeluxeEventos2.qxw")
    build_canonical_show(workspace, library)
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    families = _function_families(
        graph,
        group_fixtures(workspace.root),
        int(_functions(workspace)["Paneles Charla"].attrib["ID"]),
    )

    assert families["pixel-mode"]


def test_talk_panel_mode_and_pixel_base_keep_distinct_owners(library):
    """2026-09-02, re-review: programmed panels need a direct mode-only
    talk owner while Pixeles ON retains mode parking for other matrix fixtures.
    """
    workspace = Workspace.load(REPO / "QLC+ Setups" / "Vibra.qxw")
    build_canonical_show(workspace, library)
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    groups = group_fixtures(workspace.root)
    functions = _functions(workspace)
    talk_panel_writes = reach(graph, groups, int(functions["Paneles Charla"].attrib["ID"]))
    pixel_base_writes = reach(graph, groups, int(functions["Pixeles ON"].attrib["ID"]))

    assert talk_panel_writes
    for fixture_id, writes in talk_panel_writes.items():
        written_roles = {
            graph.capabilities[fixture_id].roles_by_offset[offset] for offset in writes
        }
        assert written_roles == {roles.EFFECT}
        assert not any(
            graph.capabilities[fixture_id].roles_by_offset[offset] == roles.EFFECT
            for offset in pixel_base_writes.get(fixture_id, {})
        )

    assert any(
        roles.EFFECT
        in {graph.capabilities[fixture_id].roles_by_offset[offset] for offset in writes}
        for fixture_id, writes in pixel_base_writes.items()
        if fixture_id not in talk_panel_writes
    ), "Pixeles ON stopped parking every non-cycle matrix fixture mode"


def test_a_moments_pixel_intensity_companion_is_not_a_second_play_hook(library):
    """2026-09-02: a moment's panel intensity support must not take over
    pixel mode or demand a duplicate PIXELES hook.
    """
    workspace = Workspace.load(REPO / "QLC+ Setups" / "DeluxeEventos2.qxw")
    build_canonical_show(workspace, library)

    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    writes = reach(
        graph,
        group_fixtures(workspace.root),
        int(_functions(workspace)["Intensidad Charla Pixeles"].attrib["ID"]),
    )
    assert not any(
        graph.capabilities[fixture_id].roles_by_offset[offset] == roles.EFFECT
        for fixture_id, offsets in writes.items()
        for offset in offsets
    )
    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert not any(f.function == "Intensidad Charla Pixeles" for f in findings)


def test_a_bare_pixel_mode_state_owner_still_requires_its_play_hook(library):
    """2026-09-02: adding a second functional pixel owner to AUTO requires
    its own PIXELES hook; an intensity-only companion must not hide it.
    """
    from lxml import etree

    from qlctool.constants import QLC_NS

    workspace = Workspace.load(REPO / "QLC+ Setups" / "DeluxeEventos2.qxw")
    build_canonical_show(workspace, library)
    functions = _functions(workspace)
    copied = _twin_scene(
        workspace,
        functions,
        "Ciclo Paneles Mixto",
        "TEST independent pixel owner",
    )
    etree.SubElement(functions["AUTO"], f"{{{QLC_NS}}}Step").text = copied.attrib["ID"]
    _family_frame(
        workspace,
        ("Rueda Colores", "Rueda Mezcla", "Luz Charla", "Ciclo Paneles Mixto"),
    )

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert any(
        f.function == "TEST independent pixel owner" and "no tiene su Toggle" in f.message
        for f in findings
    )


def test_a_nonmoving_rgb_effect_fixture_is_a_pixel_mode_owner(library):
    """2026-09-02: pixel-mode ownership follows capabilities, even if a
    fixture type omits the word "pixel".
    """
    from dataclasses import replace
    from types import SimpleNamespace

    from qlctool.checks.family_frames import _is_pixel_fixture

    workspace = Workspace.load(REPO / "QLC+ Setups" / "DeluxeEventos2.qxw")
    build_canonical_show(workspace, library)
    capability = next(
        c for c in capabilities_of(workspace.root, library) if c.fixture.fixture_id == 24
    )

    assert _is_pixel_fixture(replace(capability, fixture_type="LED PAR"))
    assert not _is_pixel_fixture(
        SimpleNamespace(is_smoke=False, roles=frozenset(capability.roles - {roles.EFFECT}))
    )
    assert not _is_pixel_fixture(
        SimpleNamespace(is_smoke=False, roles=frozenset({*capability.roles, roles.PAN}))
    )


def test_a_state_started_movement_collection_is_its_own_required_hook(library):
    """2026-09-02, play-page design: future `Movimientos Suaves` is a
    functional Collection started by a state. Its hook is required, but its
    two child movement functions are not separate hooks.
    """
    from lxml import etree

    from qlctool.constants import QLC_NS
    from qlctool.functions.collection import build_collection
    from qlctool.ids import next_function_id
    from qlctool.vc.button import build_button
    from qlctool.vc.widget_ids import next_widget_id

    workspace = Workspace.load(REPO / "QLC+ Setups" / "DeluxeEventos2.qxw")
    build_canonical_show(workspace, library)
    functions = _functions(workspace)
    washes_id = next_function_id(workspace.root)
    workspace.add_function(
        build_collection(
            washes_id, "TEST Suaves Washes", [int(functions["Suaves Washes"].attrib["ID"])]
        )
    )
    beams_id = next_function_id(workspace.root)
    workspace.add_function(
        build_collection(
            beams_id,
            "TEST Suaves Beams",
            [int(functions["Suaves Beams"].attrib["ID"])],
        )
    )
    smooth_id = next_function_id(workspace.root)
    workspace.add_function(
        build_collection(smooth_id, "TEST Movimientos Suaves", [washes_id, beams_id])
    )
    etree.SubElement(functions["AUTO"], f"{{{QLC_NS}}}Step").text = str(smooth_id)

    frame = _family_frame(workspace, ("Movimientos Suaves",))
    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert any(f.function == "TEST Movimientos Suaves" for f in findings)

    build_button(
        frame,
        next_widget_id(workspace.root),
        "TEST Movimientos Suaves",
        smooth_id,
        x=220,
        y=30,
        width=105,
        height=50,
    )
    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert not [f for f in findings if f.function in {"TEST Suaves Washes", "TEST Suaves Beams"}]


def test_a_multi_family_state_chaser_is_not_a_play_hook(library):
    """2026-09-02: Ciclo Energia coordinates several families, so a family
    frame must not demand it as a return hook for each one.
    """
    from qlctool.capabilities_of import capabilities_of
    from qlctool.checks.console_states import room_states
    from qlctool.checks.family_frames import _state_owners
    from qlctool.checks.show_graph import build_show_graph, group_fixtures

    workspace = Workspace.load(REPO / "QLC+ Setups" / "DeluxeEventos2.qxw")
    build_canonical_show(workspace, library)
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    groups = group_fixtures(workspace.root)
    states = room_states(workspace.root, graph, groups)
    owners = _state_owners(graph, groups, states)
    energy_id = int(_functions(workspace)["Ciclo Energia"].attrib["ID"])

    assert not any(energy_id in function_ids for function_ids in owners.values())


def test_an_energy_nested_owner_missing_from_its_family_frame_is_reported(library):
    """2026-09-02: an owner within an energy-cycle level remains a required
    hook, while Ciclo Energia itself stays structural and unplayable.
    """
    from lxml import etree

    from qlctool.constants import QLC_NS

    workspace = _show()
    functions = _functions(workspace)
    nested = _twin_scene(workspace, functions, "Gobo Reposo", "TEST energy gobo owner")
    level = functions["Nivel Ambiente"]
    etree.SubElement(level, f"{{{QLC_NS}}}Step").text = nested.attrib["ID"]
    _family_frame(workspace, ("Gobo Reposo",))

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert any(
        f.function == "TEST energy gobo owner" and "no tiene su Toggle" in f.message
        for f in findings
    ), "an energy-nested gobo owner went unnoticed"


def test_the_talk_owners_have_one_family_each(library):
    """2026-09-02, re-review: colour and panel-mode recovery are separate
    state owners, so a renamed frame cannot hide shared hook semantics.
    """
    from qlctool.capabilities_of import capabilities_of
    from qlctool.checks.console_states import room_states
    from qlctool.checks.family_frames import _state_owners
    from qlctool.checks.show_graph import build_show_graph, group_fixtures

    workspace = Workspace.load(REPO / "QLC+ Setups" / "DeluxeEventos2.qxw")
    build_canonical_show(workspace, library)
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    groups = group_fixtures(workspace.root)
    states = room_states(workspace.root, graph, groups)
    owners = _state_owners(graph, groups, states)
    charla_id = int(_functions(workspace)["Luz Charla"].attrib["ID"])
    panels_id = int(_functions(workspace)["Paneles Charla"].attrib["ID"])

    assert charla_id in owners["color"]
    assert charla_id not in owners["pixel-mode"]
    assert panels_id not in owners["color"]
    assert panels_id in owners["pixel-mode"]


def test_color_hooks_do_not_take_the_panel_mode_contract(library):
    """2026-09-02, re-review: graph-derived frame families keep COLOR from
    inheriting PIXELES ownership through a mode-resetting colour hook.
    """
    from qlctool.checks.family_frames import _function_families

    workspace = Workspace.load(REPO / "QLC+ Setups" / "DeluxeEventos2.qxw")
    build_canonical_show(workspace, library)
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    groups = group_fixtures(workspace.root)
    for name in ("Rueda Colores", "Rueda Mezcla", "Luz Charla"):
        families = _function_families(graph, groups, int(_functions(workspace)[name].attrib["ID"]))
        assert not families["pixel-mode"], name


def test_the_room_state_selector_is_not_a_family_handoff(library):
    """2026-09-02, re-review: selecting a whole-room state is graph-distinct
    from replacing a family hook, even though both use a SoloFrame.
    """
    workspace = Workspace.load(REPO / "QLC+ Setups" / "DeluxeEventos2.qxw")
    build_canonical_show(workspace, library)

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert not findings


def test_a_scene_only_pixel_owner_requires_its_play_hook(library):
    """2026-09-02, re-review: a direct Scene owner is still a state owner;
    only its write capability decides which JUGAR family must include it.
    """
    workspace = Workspace.load(REPO / "QLC+ Setups" / "DeluxeEventos2.qxw")
    build_canonical_show(workspace, library)
    _family_frame(workspace, ("Ciclo Paneles Mixto",), caption="renamed")

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert any(
        f.function == "Paneles Charla" and "no tiene su Toggle" in f.message for f in findings
    )


def test_a_renamed_frame_with_a_pixel_wrapper_requires_pixel_owners(library):
    """2026-09-02, re-review: a wrapper's graph writes, not the frame
    caption, choose the family contract.
    """
    workspace = Workspace.load(REPO / "QLC+ Setups" / "DeluxeEventos2.qxw")
    build_canonical_show(workspace, library)
    _family_frame(
        workspace,
        ("Rueda Colores", "Rueda Mezcla", "Luz Charla", "Jugar · Paneles - Effect 1"),
        caption="COLOR RENOMBRADO",
    )

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    missing = {f.function for f in findings if "no tiene su Toggle" in f.message}
    assert {"Ciclo Paneles Mixto", "Paneles Charla"} <= missing


def test_a_complete_renamed_pixel_frame_is_silent(library):
    """2026-09-02, re-review: the graph-derived pixel handoff does not need
    the colour wheel hooks, regardless of a frame's operator caption.
    """
    workspace = Workspace.load(REPO / "QLC+ Setups" / "DeluxeEventos2.qxw")
    build_canonical_show(workspace, library)
    _family_frame(
        workspace,
        ("Ciclo Paneles Mixto", "Paneles Charla"),
        caption="no semantic label",
    )

    findings = [f for f in check_workspace(workspace, library) if f.rule == "familia con dueño"]
    assert not findings


def test_luz_charla_keeps_momento_intensity_outside_the_color_hook(library):
    """2026-09-02: a COLOR pick stops Luz Charla but leaves Momento Charla's
    dimmer source running, while the hook still restores the beams' wheel.
    """
    workspace = Workspace.load(REPO / "QLC+ Setups" / "DeluxeEventos2.qxw")
    build_canonical_show(workspace, library)
    functions = _functions(workspace)
    charla = functions["Luz Charla"]
    moment = functions["Momento Charla"]
    beam_white_id = functions["Color Beam - White"].attrib["ID"]
    charla_base_id = functions["Luz Charla Base"].attrib["ID"]
    charla_pixel_intensity_id = functions["Intensidad Charla Pixeles"].attrib["ID"]
    intensity_id = functions["Intensidad Total"].attrib["ID"]

    assert charla.attrib["Type"] == "Collection"
    members = {step.text for step in findall_local(charla, "Step")}
    assert members == {charla_base_id, beam_white_id}
    assert intensity_id not in members
    moment_members = {step.text for step in findall_local(moment, "Step")}
    assert intensity_id in moment_members
    assert charla_pixel_intensity_id in moment_members

    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    charla_writes = reach(
        graph,
        group_fixtures(workspace.root),
        int(charla.attrib["ID"]),
    )
    assert not any(
        graph.capabilities[fixture_id].roles_by_offset[offset] in (roles.DIMMER, roles.DIMMER_FINE)
        and lit(value)
        for fixture_id, offsets in charla_writes.items()
        for offset, value in offsets.items()
    )
    pick_writes = reach(
        graph,
        group_fixtures(workspace.root),
        int(functions["Rig Rojo + Pixeles"].attrib["ID"]),
    )
    assert not any(
        graph.capabilities[fixture_id].roles_by_offset[offset] in (roles.DIMMER, roles.DIMMER_FINE)
        and lit(value)
        for fixture_id, offsets in pick_writes.items()
        for offset, value in offsets.items()
    )
    moment_writes = reach(
        graph,
        group_fixtures(workspace.root),
        int(moment.attrib["ID"]),
    )
    colour_pick_fixtures = {
        fixture_id
        for fixture_id, offsets in pick_writes.items()
        if any(
            graph.capabilities[fixture_id].roles_by_offset[offset]
            in {
                roles.RED,
                roles.GREEN,
                roles.BLUE,
            }
            for offset in offsets
        )
    }
    missing_moment_intensity = {
        fixture_id
        for fixture_id in colour_pick_fixtures
        if graph.capabilities[fixture_id].offsets_for_role(roles.DIMMER)
        and not any(
            lit(moment_writes.get(fixture_id, {}).get(offset, 0))
            for offset in graph.capabilities[fixture_id].offsets_for_role(roles.DIMMER)
        )
    }
    assert not missing_moment_intensity, (
        "a COLOR pick can still paint fixtures whose moment owns no direct intensity: "
        f"{sorted(missing_moment_intensity)}"
    )


def test_a_wrapped_colour_scene_in_a_plain_frame_still_adds_to_the_state(library):
    """2026-09-02, play-page design: a Collection wrapper must not hide a
    latched colour Scene unless it lives under complete family hooks.
    """
    workspace = _show()
    frame = _family_frame(workspace, (), solo=False)
    wrapper_id = _wrapper_button(workspace, frame, "Rojo Cabezas", "TEST wrapped red layer")

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "capa que se suma al estado"
    ]
    assert findings, "a wrapped colour layer adding to the state went unnoticed"
    assert _functions(workspace)["TEST wrapped red layer"].attrib["ID"] == str(wrapper_id)


def test_a_wrapped_pick_in_a_plain_frame_is_still_overridden(library):
    """2026-09-02, play-page design: a Collection wrapper does not make a
    plain-frame Toggle immune to the state's next gobo step.
    """
    workspace = _show()
    frame = _family_frame(workspace, (), solo=False)
    _wrapper_button(workspace, frame, "Gobo - Gobo 5", "TEST wrapped gobo layer")

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "capa pisada por el ciclo"
    ]
    assert findings, "a wrapped pick overwritten by the state went unnoticed"


def test_a_wrapped_colour_scene_in_a_plain_frame_still_leaves_a_trace(library):
    """2026-09-02, play-page design: a Collection wrapper must not hide an
    LTP colour channel no room state restores.
    """
    workspace = _show()
    for name, function in _functions(workspace).items():
        if function.attrib.get("Type") != "Scene" or name.startswith("MultiColor - "):
            continue
        for value in findall_local(function, "FixtureVal"):
            if int(value.attrib["ID"]) in BEAMS and value.text:
                pairs = _pairs_of(value)
                pairs.pop(8, None)
                _write_pairs(value, pairs)
    frame = _family_frame(workspace, (), solo=False)
    _wrapper_button(workspace, frame, "MultiColor - Todas", "TEST wrapped trace layer")

    findings = [f for f in check_workspace(workspace, library) if f.rule == "capa que deja huella"]
    assert findings, "a wrapped layer leaving an LTP trace went unnoticed"


def test_a_latched_colour_bank_on_top_of_the_running_state(library):
    """2026-09-02, cross-audit: AUTO on `Rig Cyan` plus key `1` was white on
    twenty-seven fixtures - RGB mixes HTP, so a Toggle bank adds to the
    state's colour and never shows its own. Reproduced by turning one bank
    button back into a Toggle.
    """
    workspace = _show()
    functions = _functions(workspace)
    button = _button_of(workspace, functions["Rojo Cabezas"].attrib["ID"])
    action = find_local(button, "Action")
    action.text = "Toggle"
    action.attrib.clear()

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "capa que se suma al estado"
    ]
    assert findings, "a latched colour layer adding to the state went unnoticed"
    assert "Rojo Cabezas" in {f.function for f in findings}


def test_a_strobe_whose_black_step_a_lit_state_outbids(library):
    """2026-09-02, cross-audit: STROBO was a white/black chaser and its black
    step wrote only Intensity channels, which HTP drops under a state holding
    the dimmers at 255 - white / state-colour, never white / black. Reproduced
    by rebuilding that chaser on a show-page button.
    """
    workspace = _show()
    chaser, _ = _burst_chaser(workspace, library)

    findings = [f for f in check_workspace(workspace, library) if f.rule == "estrobo sin negro"]
    assert findings, "a strobe that cannot reach black went unnoticed"
    assert chaser.attrib["Name"] in {f.function for f in findings}


def test_a_latched_layer_on_a_channel_no_state_ever_writes(library):
    """2026-09-02, cross-audit: `MultiColor - Todas` wrote the beams'
    half-colour channel to 255 and no state wrote it back, so every wheel
    colour came out split for the rest of the night. Reproduced by taking
    that channel's zero out of every scene that is not a MultiColor one, and
    turning the `Todas` button back into the Toggle it was.
    """
    workspace = _show()
    button = _button_of(workspace, _functions(workspace)["MultiColor - Todas"].attrib["ID"])
    action = find_local(button, "Action")
    action.text = "Toggle"
    action.attrib.clear()
    for name, function in _functions(workspace).items():
        if function.attrib.get("Type") != "Scene" or name.startswith("MultiColor - "):
            continue
        for value in findall_local(function, "FixtureVal"):
            if int(value.attrib["ID"]) in BEAMS and value.text:
                pairs = _pairs_of(value)
                pairs.pop(8, None)  # channel 9, the half-colour position
                _write_pairs(value, pairs)

    findings = [f for f in check_workspace(workspace, library) if f.rule == "capa que deja huella"]
    assert findings, "a latched layer nobody writes back went unnoticed"
    assert "MultiColor - Todas" in {f.function for f in findings}


def test_a_work_light_that_inherits_the_gobo_and_the_prism(library):
    """2026-09-02, cross-audit: `Todo Negro` -> `Blanco Total` after a party
    level was four white beams projecting Gobo 5 through a spinning prism,
    because the work light wrote nothing LTP. Reproduced by taking the parked
    gobo back out of it.
    """
    workspace = _show()
    for value in findall_local(_functions(workspace)["Blanco Total"], "FixtureVal"):
        if int(value.attrib["ID"]) in BEAMS and value.text:
            pairs = _pairs_of(value)
            pairs.pop(9, None)  # channel 10, the gobo wheel
            _write_pairs(value, pairs)

    findings = [f for f in check_workspace(workspace, library) if f.rule == "estado que hereda"]
    assert findings, "a state inheriting the last state's wheels went unnoticed"
    assert "Blanco Total" in {f.function for f in findings}


def test_the_fog_machines_leds_dark_for_a_whole_level(library):
    """2026-09-02, cross-audit: `Intensidad Peak` wrote the vertical fog
    machines' pump shut and nothing else, so under `Nivel Peak`, `Nivel Fiesta
    Dinamico` and `Momento Locura` the wheel coloured four LED columns whose
    dimmer nobody opened. Reproduced by taking their dimmer back out of it.
    """
    workspace = _show()
    fog = {
        int(find_local(f, "ID").text)
        for f in find_local(workspace.root, "Engine")
        if localname(f) == "Fixture"
        and (find_local(f, "Name").text or "").startswith("Humo Vertical")
    }
    assert fog
    for value in findall_local(_functions(workspace)["Intensidad Peak"], "FixtureVal"):
        if int(value.attrib["ID"]) in fog and value.text:
            pairs = _pairs_of(value)
            pairs.pop(1, None)  # channel 2, the LED master dimmer
            _write_pairs(value, pairs)

    findings = [
        f
        for f in check_workspace(workspace, library)
        if f.rule == "color sin dimmer en algun instante"
    ]
    assert findings, "a level colouring a fixture with its dimmer shut went unnoticed"
    assert "AUTO" in {f.function for f in findings}
    assert any("Humo Vertical" in fixture for f in findings for fixture in f.fixtures)


def test_a_latched_pick_the_states_chaser_steps_over(library):
    """2026-09-02, cross-audit: a gobo picked on the manual page lasted until
    `Gobo Animacion`'s next step, four seconds later, because the step's new
    fader is appended after the button's and wins the LTP channel. Reproduced
    by putting the raw gobo leaf back on a plain Toggle frame instead of its
    isolated JUGAR wrapper.
    """
    workspace = _show()
    functions = _functions(workspace)
    _family_frame(workspace, ("Gobo - Gobo 5",), solo=False)
    button = _button_of(workspace, functions["Gobo - Gobo 5"].attrib["ID"])
    action = find_local(button, "Action")
    action.text = "Toggle"
    action.attrib.clear()

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "capa pisada por el ciclo"
    ]
    assert findings, "a latched pick the state overwrites went unnoticed"
    assert "Gobo - Gobo 5" in {f.function for f in findings}


def test_a_crossfade_that_walks_a_mechanical_wheel(library):
    """2026-09-02, cross-audit: the colour wheel's 800 ms crossfade walked the
    beams' colour wheel through every detent between two colours, twenty-one
    steps every 3.3 s, all night. Reproduced by taking one beam's wheels back
    out of its <ExcludeFade>.
    """
    workspace = _show()
    fixture = next(
        f
        for f in find_local(workspace.root, "Engine")
        if localname(f) == "Fixture" and find_local(f, "ID").text == str(BEAMS[0])
    )
    exclude = find_local(fixture, "ExcludeFade")
    assert exclude is not None, "the generator no longer pins the wheels"
    fixture.remove(exclude)

    findings = [f for f in check_workspace(workspace, library) if f.rule == "rueda fundida"]
    assert findings, "a faded wheel went unnoticed"
    assert any("BEAM 230W 7R #1" in fixture for f in findings for fixture in f.fixtures)


def test_a_white_look_that_leaves_the_white_emitter_at_zero(library):
    """2026-09-02, cross-audit (Codex): every white look mixed its white out
    of red, green and blue and left the Mini Led's White channel and the MAC
    WASH's three at 0. Reproduced by taking the white back out of the work
    light on one Mini Led.
    """
    workspace = _show()
    for value in findall_local(_functions(workspace)["Blanco Total"], "FixtureVal"):
        if int(value.attrib["ID"]) == 18 and value.text:
            pairs = _pairs_of(value)
            assert pairs.pop(6, None) is not None  # channel 7, White
            _write_pairs(value, pairs)

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "blanco sin emisor blanco"
    ]
    assert findings, "an unused white emitter went unnoticed"
    assert "Blanco Total" in {f.function for f in findings}


def test_a_solo_frame_deaf_to_its_monitored_hook(library):
    """2026-09-12, found building the tablet desk: every generated solo frame
    excluded monitored buttons, so a pick never stopped the wheel AUTO had
    started (5.2.2 vcbutton.cpp:258) and the room had two colour sources. The
    checker had nothing to say about it. Reproduced by putting the flag back on
    the COLOR family frame of a generated show.
    """
    workspace = _show()
    frames = list(iter_local(workspace.root, "SoloFrame"))
    for frame in frames:
        find_local(frame, "ExcludeMonitored").text = "False"
    colour = next(f for f in frames if (f.attrib.get("Caption") or "").startswith("COLOR"))
    find_local(colour, "ExcludeMonitored").text = "True"
    findings = [f for f in check_workspace(workspace, library) if f.rule == "marco solo sordo"]
    assert findings, "a solo frame deaf to its monitored hook went unnoticed"
    assert all(f.function.startswith("COLOR") for f in findings)

    find_local(colour, "ExcludeMonitored").text = "False"
    assert not [f for f in check_workspace(workspace, library) if f.rule == "marco solo sordo"]
