"""Fixtures that animate themselves, recognised by shape and never by model."""

from pathlib import Path

from qlctool.capabilities_of import capabilities_of
from qlctool.internal_program import (
    internal_program,
    internal_program_off_pairs,
)
from qlctool.library import FixtureLibrary
from qlctool.workspace import Workspace

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "Vibra-split.qxw"
PANELS = {24, 25, 27, 28}


def _capabilities():
    workspace = Workspace.load(SHOW)
    return {
        c.fixture.fixture_id: c
        for c in capabilities_of(workspace.root, FixtureLibrary.load())
    }


def test_the_panels_carry_forty_two_programmes_of_their_own():
    caps = _capabilities()
    program = internal_program(caps[24])
    assert program is not None
    assert program.count == 42
    # Channel 6 chooses the mode, channel 7 the programme, channel 8 the speed.
    assert (program.mode_offset, program.effect_offset) == (5, 6)
    assert program.speed_offset == 7
    assert program.off_value == 0        # "No function": obey DMX colour
    assert 86 <= program.auto_value <= 171  # "Auto Mode": run its own show


def test_only_the_panels_have_them():
    """A wash with a colour macro is not a fixture that animates itself."""
    caps = _capabilities()
    with_programs = {
        fixture_id for fixture_id, capability in caps.items()
        if internal_program(capability) is not None
    }
    assert with_programs == PANELS


def test_a_fixture_with_no_programmes_needs_nothing_switched_off():
    caps = _capabilities()
    assert internal_program_off_pairs(caps[6]) == []   # a plain LED PAR
    assert internal_program_off_pairs(caps[24]) == [(5, 0)]


def test_the_number_counter_stays_out_of_the_cycle():
    """2026-08-28: the owner ran all forty-two programmes at home - "estaban
    todos menos uno que va como con un contador de numeros". The hand-built
    show's own chaser skipped exactly one of the forty-two, Effect 40, and
    that is the counter: generated for the library page, never cycled.
    """
    from qlctool.generate.builtin_effects import (
        EXCLUDED_FROM_CYCLE, generate_builtin_effects,
    )
    from qlctool.xmlutil import find_local, findall_local, localname

    workspace = Workspace.load(SHOW)
    generated = generate_builtin_effects(
        workspace,
        capabilities_of(workspace.root, FixtureLibrary.load()),
        label="Paneles",
    )
    assert len(generated.scene_ids) == 42
    functions = {
        f.attrib.get("ID"): f
        for f in find_local(workspace.root, "Engine")
        if localname(f) == "Function"
    }
    chaser = functions[str(generated.chaser_id)]
    stepped = {int(s.text) for s in findall_local(chaser, "Step")}
    assert len(stepped) == 41
    for excluded in EXCLUDED_FROM_CYCLE:
        assert generated.scene_ids[excluded - 1] not in stepped


def test_the_vertical_smoke_light_is_the_old_chaser_verbatim():
    """2026-08-28, "como el antiguo": when the vertical smoke fires, the
    panels hold Effect 1 for a minute and Effect 3 for ten - the hand-built
    console's misnamed HUMO AUTO chaser (DeluxeEventos2 ID 367), values,
    order and holds carried verbatim.
    """
    from qlctool.generate.builtin_effects import generate_builtin_effects
    from qlctool.generate.vertical_smoke_light import (
        generate_vertical_smoke_light,
    )
    from qlctool.xmlutil import find_local, findall_local, localname

    workspace = Workspace.load(SHOW)
    builtins = generate_builtin_effects(
        workspace,
        capabilities_of(workspace.root, FixtureLibrary.load()),
        label="Paneles",
    )
    chaser_id = generate_vertical_smoke_light(workspace, builtins.scene_ids)
    assert chaser_id is not None

    functions = {
        f.attrib.get("ID"): f
        for f in find_local(workspace.root, "Engine")
        if localname(f) == "Function"
    }
    chaser = functions[str(chaser_id)]
    assert chaser.attrib["Name"] == "Humo Vertical"
    assert find_local(chaser, "RunOrder").text == "Loop"
    steps = findall_local(chaser, "Step")
    assert [int(s.text) for s in steps] == [
        builtins.scene_ids[0], builtins.scene_ids[2],
    ]
    assert [int(s.attrib["Hold"]) for s in steps] == [60000, 600000]
