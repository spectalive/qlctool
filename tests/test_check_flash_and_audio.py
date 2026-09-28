"""The checks, and one test per bug that has actually happened in the room.

Split by topic out of the original `test_check.py` (over the codeality
test-file line cap): this file covers flash and strobe coverage, dimmers
shadowed by HTP, and the console's audio triggers.
"""

import pytest
from burst_chaser import burst_chaser as _burst_chaser
from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions
from named_show import named_show as _show

from qlctool.checks.check_workspace import check_workspace
from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.localname import localname

BEAMS = (20, 21, 22, 23)


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


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
