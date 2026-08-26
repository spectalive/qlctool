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
        # Every step of the rig-wide colour wheel: the solid colours and the
        # movers-against-the-rest contrasts alike.
        if function.attrib.get("Path") != "Colores Rig":
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

    Reproduced the way the owner hit it: put the pixel groups back on the
    rig-wide wheel while their own matrix cycle is still running under AUTO.
    """
    workspace = _show()
    functions = _functions(workspace)
    scene = functions["Rig Rojo"]
    value = find_local(scene, "FixtureVal")
    # Fixture 2 is an LED Bar: pure RGB, and painted by Ciclo Matrices.
    duplicate = value.makeelement(value.tag, {"ID": "2"})
    duplicate.text = "0,255,1,0,2,0"
    scene.append(duplicate)

    findings = [
        f for f in check_workspace(workspace, library) if f.rule == "colores pisados"
    ]
    assert any(f.function == "AUTO" for f in findings), (
        "two colour sources on one bar under AUTO went unnoticed"
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
