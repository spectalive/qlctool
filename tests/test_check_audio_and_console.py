"""The checks, and one test per bug that has actually happened in the room.

Split by topic out of the original `test_check.py` (over the codeality
test-file line cap): this file covers the audio triggers' binding rules and
the console's MIDI bindings.
"""

import pytest
from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions
from named_show import named_show as _show

from qlctool.checks.check_workspace import check_workspace
from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.localname import localname


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


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
