"""The JUGAR play page's reset strip, and the Control desk it must not empty.

Split by topic out of the original `test_live_console.py` (over the codeality
test-file line cap).
"""

import pytest
from buttons_of import buttons_of as _buttons
from console_frame_of import console_frame_of as _console_frame
from frame_named import frame_named as _frame_named
from function_id_of import function_id_of as _function_id
from functions_by_id_of_root import functions_by_id_of_root as _functions_by_id
from rig_root import RIG_ROOT
from walk_widgets import walk_widgets as _walk

from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.generate.build_canonical_show import build_canonical_show
from qlctool.generate.console_layout import GRAND_MASTER_LINES, PAGE_CONTROL
from qlctool.leading_glyph import leading_glyph
from qlctool.localname import localname
from qlctool.names.default_names import default_names
from qlctool.palette import PRIMARY_COLORS
from qlctool.workspace import Workspace

REPO = RIG_ROOT
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"


@pytest.fixture(scope="module")
def console(tmp_path_factory):
    ws = Workspace.load(SHOW)
    build_canonical_show(ws, FixtureLibrary.load())
    out = tmp_path_factory.mktemp("console") / "Vibra.qxw"
    ws.save(out)
    root = Workspace.load(out).root
    return root, find_local(find_local(root, "VirtualConsole"), "Frame")


def _console_page(widget, console_frame):
    current = widget
    while current.getparent() is not console_frame:
        current = current.getparent()
        assert current is not None
    return int(current.attrib.get("Page", "0"))


def test_the_play_strip_is_keyless_binding_free_and_has_only_safe_actions(console):
    """2026-09-02: the reset strip duplicates controls without duplicating panic state."""
    root, outer = console
    functions = _functions_by_id(root)
    strip = _frame_named(outer, "VOLVER AL SHOW")
    buttons = _buttons(strip)
    names = [functions[_function_id(button)].attrib["Name"] for button in buttons]
    assert names == [
        "AUTO",
        "Momento Charla",
        "Momento Tranquilo",
        "Momento Fiesta",
        "Momento Locura",
        "Blanco Total",
        "Todo Negro",
        "Flash 100%",
        "Flash Color",
        "Humo ON",
        "Strobo Rapido",
    ]
    for button in buttons:
        key = find_local(button, "Key")
        action = find_local(button, "Action")
        assert key is None or not key.text
        assert not findall_local(button, "Input")
        assert (action.text or "").strip() not in ("Blackout", "StopAll")


def test_every_play_pick_and_reset_strip_is_keyless(console):
    """2026-09-02: picks and duplicated reset controls have no key bindings."""
    root, outer = console
    functions = _functions_by_id(root)
    hook_names = {
        "Rueda Colores",
        "Rueda Simples",
        "Rueda Pastel",
        "Rueda Multicolor",
        "Rueda Mezcla",
        "Luz Charla",
        "Arcoiris Simultaneo",
        "Arcoiris Pasos",
        "Ciclo Paneles Mixto",
        "Paneles Charla",
        "Movimientos Suaves",
        "Movimientos Cabezas",
        "Movimientos Rapidos",
        "Cabezas Centro",
        "Gobo Animacion",
        "Gobo Reposo",
        "Prisma Animacion",
        "Prisma Reposo",
    }
    buttons = _buttons(_frame_named(outer, "VOLVER AL SHOW"))
    for caption in ("COLOR", "PIXELES", "CABEZAS", "GOBOS", "PRISMA"):
        for button in _buttons(_frame_named(outer, caption)):
            name = functions[_function_id(button)].attrib["Name"].removeprefix("Jugar · ")
            if name not in hook_names:
                buttons.append(button)
    assert buttons
    for button in buttons:
        state = find_local(button, "WindowState")
        assert int(state.attrib["Width"]) >= 60, button.attrib.get("Caption")
        assert int(state.attrib["Height"]) >= 44, button.attrib.get("Caption")
        key = find_local(button, "Key")
        assert key is None or not key.text, button.attrib.get("Caption")


def test_every_play_button_fits_its_immediate_family_frame(console):
    """2026-09-02, re-review: JUGAR's 15 pixel controls must fit their own
    frame, not merely the console canvas.
    """
    _, outer = console
    for caption in ("COLOR", "PIXELES", "CABEZAS", "GOBOS", "PRISMA"):
        family = _frame_named(outer, caption)
        for parent in (
            widget for widget in family.iter() if localname(widget) in ("Frame", "SoloFrame")
        ):
            parent_state = find_local(parent, "WindowState")
            parent_width = int(parent_state.attrib["Width"])
            parent_height = int(parent_state.attrib["Height"])
            for button in (child for child in parent if localname(child) == "Button"):
                assert button.getparent() is parent, (caption, button.attrib.get("Caption"))
                state = find_local(button, "WindowState")
                x = int(state.attrib["X"])
                y = int(state.attrib["Y"])
                assert x >= 0 and x + int(state.attrib["Width"]) <= parent_width
                assert y >= 0 and y + int(state.attrib["Height"]) <= parent_height


def test_the_smc_pad_bindings_follow_the_play_hooks(console):
    """2026-09-02: bank-two hardware follows the hooks, while picks stay unbound."""
    from qlctool.generate.smc_pad_bindings import SMC_PAD_BINDINGS

    _, outer = console
    captions = {
        "Colores completos · W": "colour_wheel",
        "Mezcla · E": "mix_wheel",
        "AUTO normal · A": "head_movements",
        "AUTO gobos · G": "gobo_animation",
        "AUTO prisma · P": "prism_animation",
        "Arcoiris junto · '": "rainbow_together",
        "Arcoiris fases · ¡": "rainbow_steps",
    }
    play_widgets = [child for child in _console_frame(outer) if child.attrib.get("Page") == "1"]
    buttons = [button for widget in play_widgets for button in _buttons(widget)]
    bound = {}
    for button in buttons:
        inputs = [source for source in findall_local(button, "Input") if "Channel" in source.attrib]
        if inputs:
            assert len(inputs) == 1
            bound[leading_glyph(button.attrib["Caption"])[1]] = int(inputs[0].attrib["Channel"])
    assert bound == {caption: SMC_PAD_BINDINGS[name] for caption, name in captions.items()}


def test_colour_hits_force_their_colour_over_the_running_state(console):
    """2026-09-02: held colour hits override priority and HTP colour mixing."""
    root, outer = console
    functions = _functions_by_id(root)
    hits = _frame_named(outer, "GOLPES DE COLOR")
    buttons = _buttons(hits)
    assert [functions[_function_id(button)].attrib["Name"] for button in buttons] == [
        f"Golpe {name}" for name in PRIMARY_COLORS
    ]
    for button in buttons:
        action = find_local(button, "Action")
        assert action.text == "Flash"
        assert action.attrib.get("Override") == "1"
        assert action.attrib.get("ForceLTP") == "1"


def test_control_retains_every_direct_operator_contract(console):
    """2026-09-02: moving families to JUGAR must not empty the Control desk."""
    from qlctool.generate.smc_pad_bindings import SMC_PAD_BINDINGS
    from qlctool.vibra.keys import KEYS

    root, root_frame = console
    console_frame = _console_frame(root_frame)
    functions = _functions_by_id(root)
    widgets = [widget for widget, _, _ in _walk(root_frame)]

    def named(tag, caption):
        matches = [
            widget
            for widget in widgets
            if localname(widget) == tag
            and leading_glyph(widget.attrib.get("Caption", ""))[1].startswith(caption)
        ]
        assert len(matches) == 1, (tag, caption)
        assert _console_page(matches[0], console_frame) == PAGE_CONTROL
        return matches[0]

    contracts = (
        ("XYPad", "Cabezas"),
        ("SpeedDial", "Vel. Movimiento"),
        ("Slider", "Master General"),
        ("Button", "GOLPE GRAVES"),
        ("Frame", "Intensidad y strobo de fixture"),
        ("Frame", "Color de los BEAM"),
        ("AudioTriggers", "Audio"),
    )
    retained = {(tag, caption): named(tag, caption) for tag, caption in contracts}
    # 2026-09-25: no vertical column is patched here, so no column light and
    # no button for it (`tests/test_vertical_smoke_columns.py`).
    assert not [
        w
        for w in widgets
        if localname(w) == "Button"
        and leading_glyph(w.attrib.get("Caption", ""))[1].startswith("HUMO VERTICAL")
    ]

    movement_dial = retained[("SpeedDial", "Vel. Movimiento")]
    dial_inputs = list(findall_local(movement_dial, "Input"))
    assert {source.attrib.get("Key") for source in dial_inputs} >= {"M"}
    assert {
        int(source.attrib["Channel"]) for source in dial_inputs if "Channel" in source.attrib
    } == {SMC_PAD_BINDINGS["movement_speed"]}

    grand_master = retained[("Slider", "Master General")]
    assert find_local(grand_master, "SliderMode").text == "GrandMaster"
    assert [
        int(source.attrib["Channel"])
        for source in findall_local(grand_master, "Input")
        if "Channel" in source.attrib
    ] == [SMC_PAD_BINDINGS["grand_master"]]
    control_labels = {
        widget.attrib.get("Caption", "")
        for widget in widgets
        if localname(widget) == "Label" and _console_page(widget, console_frame) == PAGE_CONTROL
    }
    assert {default_names().display(line) for line in GRAND_MASTER_LINES} <= control_labels

    bass = retained[("Button", "GOLPE GRAVES")]
    assert functions[_function_id(bass)].attrib["Name"] == "Golpe Graves"
    assert find_local(bass, "Action").text == "Flash"
    assert not (find_local(bass, "Key").text or "")

    dimmer_names = (
        "Dimmer Chase",
        "Dimmer Chase 2",
        "Dimmer PingPong",
        "Dimmer Secuencia",
        "Strobo ON",
        "Strobo OFF",
    )
    dimmer_frame = retained[("Frame", "Intensidad y strobo de fixture")]
    for dimmer in _buttons(dimmer_frame):
        name = functions[_function_id(dimmer)].attrib["Name"]
        assert name in dimmer_names
        assert find_local(dimmer, "Action").text == "Toggle"
        assert find_local(dimmer, "Key").text == KEYS[name]
        assert not findall_local(dimmer, "Input")
    assert {
        functions[_function_id(button)].attrib["Name"] for button in _buttons(dimmer_frame)
    } == set(dimmer_names)

    beam_frame = retained[("Frame", "Color de los BEAM")]
    assert _buttons(beam_frame)
    for beam_pick in _buttons(beam_frame):
        action = find_local(beam_pick, "Action")
        assert action.text == "Flash"
        assert action.attrib.get("Override") == "1"
        assert not (find_local(beam_pick, "Key").text or "")
        assert not findall_local(beam_pick, "Input")

    banks = [
        widget
        for widget in widgets
        if localname(widget) == "Frame" and widget.attrib.get("Caption", "").startswith("Colores ")
    ]
    assert banks
    for bank in banks:
        assert _console_page(bank, console_frame) == PAGE_CONTROL
        keyed = [button for button in _buttons(bank) if find_local(button, "Key").text]
        assert [find_local(button, "Key").text for button in keyed] == list("1234567890")
        for colour in _buttons(bank):
            action = find_local(colour, "Action")
            assert action.text == "Flash"
            assert action.attrib.get("Override") == "1"
            assert action.attrib.get("ForceLTP") == "1"
            assert not findall_local(colour, "Input")


def test_control_middle_column_reflows_without_a_vertical_hole(console):
    """2026-09-03: beam colour and aiming controls form one usable column."""
    _, root_frame = console
    widgets = [widget for widget, _, _ in _walk(root_frame)]

    def state_for(tag, caption):
        matches = [
            widget
            for widget in widgets
            if localname(widget) == tag and widget.attrib.get("Caption", "").startswith(caption)
        ]
        assert len(matches) == 1, (tag, caption)
        return find_local(matches[0], "WindowState")

    beam = state_for("Frame", "Color de los BEAM")
    guidance = state_for("Label", "Apunta las cabezas")
    pad = state_for("XYPad", "Cabezas")

    def geometry(state):
        return tuple(int(state.attrib[name]) for name in ("X", "Y", "Width", "Height"))

    assert geometry(beam) == (540, 68, 628, 150)
    assert geometry(guidance) == (540, 224, 628, 20)
    assert geometry(pad) == (540, 250, 628, 636)
