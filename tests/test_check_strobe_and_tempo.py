"""The checks, and one test per bug that has actually happened in the room.

Split by topic out of the original `test_check.py` (over the codeality
test-file line cap): this file covers strobe safety and speed, and the tap
dials and Tempo tags that drive a chaser's timing.
"""

import pytest
from burst_chaser import burst_chaser as _burst_chaser
from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions
from named_show import named_show as _show

from qlctool.capabilities_of import capabilities_of
from qlctool.checks.check_workspace import check_workspace
from qlctool.checks.strobe_capable_offsets import strobe_capable_offsets
from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.iter_local import iter_local
from qlctool.localname import localname


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


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
    wash figures split on `keeps_16bit`), and `Collection::write` hands the
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
