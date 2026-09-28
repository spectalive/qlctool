"""The checks, and one test per bug that has actually happened in the room.

Split by topic out of the original `test_check.py` (over the codeality
test-file line cap): this file covers Collection wrappers and latched Toggle
layers hiding behind a plain frame or a running room state, plus a solo frame
left deaf to its own monitored hook.
"""

import pytest
from burst_chaser import burst_chaser as _burst_chaser
from button_of import button_of as _button_of
from family_frame import family_frame as _family_frame
from fixture_val_pairs import fixture_val_pairs as _pairs_of
from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions
from named_show import named_show as _show
from wrapper_button import wrapper_button as _wrapper_button
from write_fixture_val_pairs import write_fixture_val_pairs as _write_pairs

from qlctool.checks.check_workspace import check_workspace
from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.iter_local import iter_local
from qlctool.localname import localname

BEAMS = (20, 21, 22, 23)


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


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
