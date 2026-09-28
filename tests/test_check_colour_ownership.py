"""The checks, and one test per bug that has actually happened in the room.

This file is the discipline the show is now built on: **a malfunction is not
fixed until a check can see it**. Every regression below is a night that went
wrong - beams that stayed black, panels that were the right colour and off, a
room that went white when two levels were pressed - reproduced by putting the
bug back into a generated show and asserting the checker still bites.

The first test is the gate: every workspace the repo ships is run through every
rule. New rules therefore have to be true of all three shows at once, which is
what stops a check from being written to fit one file.

Split by topic out of the original `test_check.py` (over the codeality
test-file line cap): this file covers colour ownership - one clock, one
source, and every fixture that owns a wheel step actually lit.
"""

import pytest
from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions
from named_show import named_show as _show

from qlctool.checks.build_show_graph import build_show_graph
from qlctool.checks.check_workspace import check_workspace
from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.iter_local import iter_local

SHOWS = ("Vibra.qxw", "Vibra-beats.qxw", "Vibra-split.qxw")
BEAMS = (20, 21, 22, 23)

# Findings the shipped shows are allowed to carry. Empty, and meant to stay
# that way: an entry here is a known-broken button somebody will press.
KNOWN: set[tuple[str, str]] = set()


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


def test_2026_09_13_desk_link_loss_requires_bounded_hits():
    """Tablet bench night: losing a Flash release left its scene running."""
    from qlctool.checks.rule_desk_bursts import check_desk_bursts
    from qlctool.names.default_names import default_names

    burst_frame = default_names().display("desk_bursts")
    workspace = _show()
    for frame in list(iter_local(workspace.root, "Frame")):
        if frame.get("Caption") == burst_frame:
            frame.getparent().remove(frame)
    graph = build_show_graph(workspace.root, [])
    findings = check_desk_bursts(graph, workspace.root)
    assert len(findings) == 17
    assert {f.function for f in findings} >= {"humo-ya", "humo-vert", "flash", "rojo"}


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
