"""The checks, and one test per bug that has actually happened in the room.

Split by topic out of the original `test_check.py` (over the codeality
test-file line cap): this file covers the console (solo frames, shared keys,
widgets spilling past their own parent) and the smoke machines' pump/light
contract.
"""

import pytest
from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions
from named_show import named_show as _show

from qlctool.checks.check_workspace import check_workspace
from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_groups import fixture_groups
from qlctool.fixture_library import FixtureLibrary
from qlctool.fog_offsets import fog_offsets
from qlctool.localname import localname

BEAMS = (20, 21, 22, 23)


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


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
                for offset, level in zip(numbers[0::2], numbers[1::2], strict=True)
                if offset in machines[fixture_id]
            ]
            if kept:
                value.text = ",".join(str(n) for pair in kept for n in pair)
            else:
                value.getparent().remove(value)

    findings = [f for f in check_workspace(workspace, library) if f.rule == "humo-luz"]
    assert findings, "the stripped show should read as a dark column"
