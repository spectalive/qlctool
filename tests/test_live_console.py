"""The console the show is run from: one screen, and no frame that kills itself.

Two things are checked here that a workspace loading cleanly in QLC+ will not
catch. First that everything fits a 13" laptop, because a console taller than
the screen is unusable at a venue. Second the solo-frame rule: a solo frame
stops every other widget's function the moment one starts, so a function and
anything it starts must never share one - that is what made AUTO die the
instant it was pressed.
"""

from pathlib import Path

import pytest

from qlctool.generate.canonical_show import KEYS, build_canonical_show
from qlctool.generate.live_console import (
    BIG_FONT,
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    GRAND_MASTER_LINES,
    HITS,
    PAGE_CONTROL,
    ROOM_STATES,
)
from qlctool.library import FixtureLibrary
from qlctool.palette import PRIMARY_COLORS
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, localname

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"

# Buttons that exist only when the rig has the fixture behind them. The test
# rig is the hand-built DeluxeEventos2, which has no lit fog machine, so its
# console builds without the vertical burst.
OPTIONAL_KEYS = {"Humo Vertical YA"}

WIDGET_TAGS = {
    "Frame",
    "SoloFrame",
    "Button",
    "Label",
    "Slider",
    "XYPad",
    "SpeedDial",
    "AudioTriggers",
    "Matrix",
    "Clock",
}


@pytest.fixture(scope="module")
def console(tmp_path_factory):
    ws = Workspace.load(SHOW)
    build_canonical_show(ws, FixtureLibrary.load())
    out = tmp_path_factory.mktemp("console") / "Vibra.qxw"
    ws.save(out)
    root = Workspace.load(out).root
    return root, find_local(find_local(root, "VirtualConsole"), "Frame")


def _members(root):
    """function id -> the function ids it starts, transitively."""
    direct = {}
    for function in find_local(root, "Engine"):
        if localname(function) != "Function":
            continue
        if function.attrib.get("Type") not in ("Chaser", "Collection", "Sequence"):
            continue
        direct[int(function.attrib["ID"])] = {
            int(step.text) for step in findall_local(function, "Step") if step.text
        }

    def expand(fid, seen):
        for member in direct.get(fid, ()):
            if member in seen:
                continue
            seen.add(member)
            expand(member, seen)
        return seen

    return {fid: expand(fid, set()) for fid in direct}


def _walk(widget, x=0, y=0):
    """Every widget with its absolute position on the canvas."""
    for child in widget:
        if localname(child) not in WIDGET_TAGS:
            continue
        state = find_local(child, "WindowState")
        cx = x + int(state.attrib["X"])
        cy = y + int(state.attrib["Y"])
        yield child, cx, cy
        yield from _walk(child, cx, cy)


def test_the_console_fits_a_thirteen_inch_screen(console):
    root, frame = console
    size = find_local(find_local(root, "VirtualConsole"), "Properties")
    size = find_local(size, "Size")
    assert (int(size.attrib["Width"]), int(size.attrib["Height"])) == (
        CANVAS_WIDTH,
        CANVAS_HEIGHT,
    )

    for widget, x, y in _walk(frame):
        state = find_local(widget, "WindowState")
        right = x + int(state.attrib["Width"])
        bottom = y + int(state.attrib["Height"])
        assert right <= CANVAS_WIDTH, (widget.attrib.get("Caption"), right)
        assert bottom <= CANVAS_HEIGHT, (widget.attrib.get("Caption"), bottom)


def test_no_solo_frame_holds_a_function_and_what_it_starts(console):
    """A member starting is what makes its solo frame stop the parent."""
    root, frame = console
    members = _members(root)

    for widget, _, _ in _walk(frame):
        if localname(widget) != "SoloFrame":
            continue
        inside = {
            int(find_local(b, "Function").attrib["ID"]) for b in widget if localname(b) == "Button"
        }
        for function_id in inside:
            clash = inside & members.get(function_id, set())
            assert not clash, (widget.attrib.get("Caption"), function_id, clash)


def test_only_blackout_buttons_need_unique_local_state(console):
    _, frame = console
    blackouts = [
        b
        for b, _, _ in _walk(frame)
        if localname(b) == "Button"
        and (action := find_local(b, "Action")) is not None
        and (action.text or "").strip() == "Blackout"
    ]
    assert len(blackouts) <= 1


def test_multipage_frames_only_reference_pages_they_have(console):
    _, frame = console
    pages = 0
    for widget, _, _ in _walk(frame):
        multipage = find_local(widget, "Multipage")
        if multipage is None:
            continue
        pages += 1
        total = int(multipage.attrib["PagesNum"])
        assert total > 1
        for child in widget:
            if localname(child) not in WIDGET_TAGS:
                continue
            assert 0 <= int(child.attrib.get("Page", "0")) < total
    assert pages == 4  # the console, gobo picks, mixes and matrices


def test_the_keyboard_survives(console):
    _, frame = console
    by_key = {}
    for widget, _, _ in _walk(frame):
        if localname(widget) != "Button":
            continue
        key = find_local(widget, "Key")
        if key is not None and key.text:
            by_key.setdefault(key.text, []).append(widget.attrib.get("Caption"))

    for name, key in KEYS.items():
        if name in OPTIONAL_KEYS and key not in by_key:
            continue
        assert key in by_key, name
    # 1-0 light the same colour on all three banks, as the old console does.
    assert len(by_key["1"]) == 3
    # Everything else is one key, one look: every widget sees every key
    # press, so two buttons sharing a letter would fire both.
    for key, captions in by_key.items():
        if key in "1234567890":
            continue
        assert len(captions) == 1, (key, captions)


def test_the_bass_band_presses_a_flash_hit_and_never_a_strobe(console):
    """2026-08-27: the bass band is bound, and the target has to be a Flash
    hit, not a Toggle. An audio bar calls `pressFunction` on the way up and
    `pressFunction`+`releaseFunction` on the way down (`ui/src/audiobar.cpp`
    in the QLC+ source) - exactly how a Flash button expects to be worked, so
    it self-releases. A Toggle would stay latched one way or the other, and a
    Toggle inside the room-state solo frame (`Blanco Total`, the first shape
    this bug took) would also stop AUTO with nothing to restart it -
    `disparador de audio vacio` in checks/ catches that shape directly; this
    test pins the generator's own output.
    """
    _, frame = console
    buttons = {int(w.attrib["ID"]): w for w, _, _ in _walk(frame) if localname(w) == "Button"}
    triggers = [w for w, _, _ in _walk(frame) if localname(w) == "AudioTriggers"]
    assert len(triggers) == 1

    bars = findall_local(triggers[0], "SpectrumBar")
    assert len(bars) == 1, "exactly one band should ship bound"
    bar = bars[0]
    assert bar.attrib["Type"] == "3"  # AudioBar::VCWidgetBar
    target = buttons[int(bar.attrib["WidgetID"])]
    assert find_local(target, "Action").text == "Flash", bar.attrib["Name"]
    caption = target.attrib.get("Caption", "")
    assert "STROBO" not in caption.upper(), caption


def _frame_named(frame, caption):
    for widget, _, _ in _walk(frame):
        if localname(widget) in ("Frame", "SoloFrame") and widget.attrib.get(
            "Caption", ""
        ).startswith(caption):
            return widget
    raise AssertionError(f"no frame captioned {caption!r}")


def _captions(widget):
    return [child.attrib.get("Caption", "") for child in widget if localname(child) == "Button"]


def _functions_by_id(root):
    return {
        int(function.attrib["ID"]): function
        for function in find_local(root, "Engine")
        if localname(function) == "Function" and "ID" in function.attrib
    }


def _buttons(widget):
    return [child for child in widget.iter() if localname(child) == "Button"]


def _function_id(button):
    return int(find_local(button, "Function").attrib["ID"])


def _console_frame(root_frame):
    return next(
        widget
        for widget, _, _ in _walk(root_frame)
        if localname(widget) == "Frame"
        and (multipage := find_local(widget, "Multipage")) is not None
        and multipage.attrib["PagesNum"] == "4"
    )


def _console_page(widget, console_frame):
    current = widget
    while current.getparent() is not console_frame:
        current = current.getparent()
        assert current is not None
    return int(current.attrib.get("Page", "0"))


def test_the_room_is_in_exactly_one_state(console):
    """AUTO, the moments, the work light and the blackout are one solo frame.

    That is the fix for the thing that broke the show: two energy levels
    pressed at once put two colour beds and two movement sources on the same
    rig, and the room went white. A state cannot be stacked if starting one
    stops the others.
    """
    _, frame = console
    room = _frame_named(frame, "LA SALA ESTÁ ASÍ")
    assert localname(room) == "SoloFrame"
    assert _captions(room) == [caption for _, caption, _, _ in ROOM_STATES]


def test_no_energy_level_is_a_button(console):
    """The levels are what the cycle steps, not something to press.

    Pressing one by hand while AUTO ran gave that level two owners and left the
    other one running underneath - which is exactly what the operator hit.
    """
    root, frame = console
    functions = {
        int(f.attrib["ID"]): f.attrib.get("Name", "")
        for f in find_local(root, "Engine")
        if localname(f) == "Function" and f.attrib.get("ID")
    }
    driven = {
        functions.get(int(find_local(b, "Function").attrib["ID"]), "")
        for b, _, _ in _walk(frame)
        if localname(b) == "Button"
    }
    assert not {n for n in driven if n.startswith("Nivel ")}
    assert "Ciclo Energia" not in driven


def test_the_panic_button_stops_everything_and_drives_nothing(console):
    _, frame = console
    panic = _frame_named(frame, "SI ALGO VA MAL")
    buttons = [b for b in panic if localname(b) == "Button"]
    stop_all = [b for b in buttons if find_local(b, "Action").text == "StopAll"]
    assert len(stop_all) == 1
    action = find_local(stop_all[0], "Action")
    assert int(action.attrib["FadeOut"]) > 0
    # Function::invalidId(): it stops what is running rather than adding to it.
    assert find_local(stop_all[0], "Function").attrib["ID"] == "4294967295"


def test_the_panic_frame_also_has_a_blackout_button(console):
    """StopAll stops functions; Blackout forces the outputs themselves to zero.

    They answer different questions - "what is running" versus "what is the
    desk outputting" - so the panic frame needs both, not one standing in for
    the other.
    """
    _, frame = console
    panic = _frame_named(frame, "SI ALGO VA MAL")
    buttons = [b for b in panic if localname(b) == "Button"]
    blackout = [b for b in buttons if find_local(b, "Action").text == "Blackout"]
    assert len(blackout) == 1
    # No function of its own, same as StopAll.
    assert find_local(blackout[0], "Function").attrib["ID"] == "4294967295"
    stop_all = [b for b in buttons if find_local(b, "Action").text == "StopAll"]
    assert len(stop_all) == 1


def test_every_button_on_the_show_page_says_its_own_key(console):
    """Nobody reads a key map at a venue: the key is on the button."""
    _, frame = console
    for caption in _captions(_frame_named(frame, "LA SALA ESTÁ ASÍ")) + _captions(
        _frame_named(frame, "GOLPES")
    ):
        assert " · " in caption, caption
    actual = _captions(_frame_named(frame, "GOLPES"))
    expected = [caption for name, caption in HITS if name not in OPTIONAL_KEYS or caption in actual]
    assert expected == actual


def test_a_colour_button_says_which_colour_it_is(console):
    """Thirty blank squares is what the three colour banks used to be.

    2026-08-28: twelve buttons per bank since keys 9/0 went back to the old
    blue/red splits - ten keyed (eight solids + the two splits), plus the two
    displaced solids keyless at the end.
    """
    _, frame = console
    for group in ("BarrasLed", "Cabezas", "PAR"):
        bank = _frame_named(frame, f"Colores {group}")
        captions = _captions(bank)
        assert len(captions) == 12
        assert all(captions), group
        assert len(set(captions)) == 12, group
        assert "Az/Ro" in captions and "Ro/Az" in captions, group


def test_the_console_can_reach_the_grand_master(console):
    """The workspace's <GrandMaster> had no widget bound to it at all.

    QLC+ moves that value through a Slider whose SliderMode is GrandMaster,
    not the usual Level/Adjust/Submaster - confirmed to load on the installed
    5.2.2 binary (docs/qlc5-verification.md, probe-gm-slider.qxw).
    """
    _, frame = console
    sliders = [w for w, _, _ in _walk(frame) if localname(w) == "Slider"]
    modes = {(find_local(s, "SliderMode").text or ""): find_local(s, "SliderMode") for s in sliders}
    # Exactly one GrandMaster; the Level fader over the panels' speed channel
    # ("Vel. Paneles", 2026-08-27) rides beside it and must not absorb it.
    assert sorted(modes) == ["GrandMaster", "Level"]
    assert modes["GrandMaster"].attrib["ValueDisplayStyle"] == "Exact"


def test_a_mix_button_is_not_ambiguous(console):
    """Azul and Amarillo both start with an A: one letter labelled six pairs
    of different buttons identically."""
    _, frame = console
    mixes = _frame_named(frame, "Mezclas de dos colores")
    by_page = {}
    for child in mixes:
        if localname(child) != "Button":
            continue
        by_page.setdefault(child.attrib.get("Page", "0"), []).append(child.attrib["Caption"])
    assert by_page
    for page, captions in by_page.items():
        assert len(captions) == len(set(captions)), page


def test_the_colour_banks_shrink_instead_of_running_off_the_screen():
    """2026-08-31: a fifth fixture group (the two MAC WASH) added a fifth
    colour bank to the manual page's left column, and the column was stacked at
    a hard-coded 128px pitch. Everything under it - the four dimmer chases and
    both strobe buttons - went off the bottom of a 900px screen, unreachable,
    while the generator's own summary still said "on one 1440x900 screen".

    The pitch now comes from the room left between the layers above and the
    dimmer frame below, so the column fits whatever the rig grows into.
    """
    from qlctool.vc.bank_pitch import (
        BANK_COLUMN_TOP,
        BANK_PITCH_TOP,
        DIMMER_FRAME_HEIGHT,
        OUTER_HEIGHT,
        bank_pitch_for,
    )

    for banks in range(1, 12):
        pitch = bank_pitch_for(banks)
        assert pitch <= BANK_PITCH_TOP
        bottom = BANK_COLUMN_TOP + banks * pitch + DIMMER_FRAME_HEIGHT
        assert bottom <= OUTER_HEIGHT, (
            f"{banks} colour banks push the column {bottom - OUTER_HEIGHT}px "
            f"past the bottom of the screen"
        )


def test_the_play_page_and_gobo_picker_declare_their_pages(console):
    """2026-09-02: JUGAR is page two and gobos remain legible on two inner pages."""
    _, outer = console
    console_frame = _console_frame(outer)

    play_labels = [
        widget
        for widget in console_frame
        if localname(widget) == "Label" and widget.attrib.get("Caption", "").startswith("2 · JUGAR")
    ]
    assert len(play_labels) == 1
    assert play_labels[0].attrib.get("Page") == "1"

    gobos = _frame_named(outer, "GOBOS")
    inner = next(
        child
        for child in gobos
        if localname(child) == "Frame" and find_local(child, "Multipage") is not None
    )
    assert find_local(inner, "Multipage").attrib["PagesNum"] == "2"

    strip = _frame_named(outer, "VOLVER AL SHOW")
    assert localname(strip) == "Frame"


def test_every_play_family_is_solo_and_starts_with_its_hooks(console):
    """2026-09-02: each family has every state owner before any manual pick."""
    root, outer = console
    functions = _functions_by_id(root)
    expected = {
        "COLOR": (
            ("Rueda Colores", "AUTO colores · W"),
            ("Rueda Mezcla", "Mezcla · E"),
            ("Luz Charla", "Luz Charla"),
        ),
        "PIXELES": (
            ("Ciclo Paneles Mixto", "AUTO paneles"),
            ("Paneles Charla", "Paneles Charla"),
        ),
        "CABEZAS": (
            ("Movimientos Suaves", "AUTO lento"),
            ("Movimientos Cabezas", "AUTO normal · A"),
            ("Movimientos Rapidos", "AUTO rapido"),
            ("Cabezas Centro", "Centro"),
        ),
        "GOBOS": (("Gobo Animacion", "AUTO gobos · G"), ("Gobo Reposo", "Reposo")),
        "PRISMA": (("Prisma Animacion", "AUTO prisma · P"), ("Prisma Reposo", "Reposo")),
    }
    for caption, hooks in expected.items():
        family = _frame_named(outer, caption)
        assert localname(family) == "SoloFrame"
        buttons = _buttons(family)
        names = [functions[_function_id(button)].attrib["Name"] for button in buttons]
        assert names[: len(hooks)] == [name for name, _ in hooks], caption
        assert [button.attrib["Caption"] for button in buttons[: len(hooks)]] == [
            hook_caption for _, hook_caption in hooks
        ]
        for hook in buttons[: len(hooks)]:
            appearance = find_local(hook, "Appearance")
            assert find_local(appearance, "Font").text == BIG_FONT
            assert find_local(appearance, "BackgroundColor").text != "Default"


def test_the_seven_play_hooks_restore_their_global_keys_and_captions(console):
    """2026-09-02: the operator's seven JUGAR shortcuts are exact."""
    root, outer = console
    functions = _functions_by_id(root)
    expected = {
        "Rueda Colores": ("AUTO colores · W", "W"),
        "Rueda Mezcla": ("Mezcla · E", "E"),
        "Movimientos Cabezas": ("AUTO normal · A", "A"),
        "Gobo Animacion": ("AUTO gobos · G", "G"),
        "Prisma Animacion": ("AUTO prisma · P", "P"),
        "Arcoiris Simultaneo": ("Arcoiris junto · '", "'"),
        "Arcoiris Pasos": ("Arcoiris fases · ¡", "¡"),
    }
    actual = {}
    play_widgets = [child for child in _console_frame(outer) if child.get("Page") == "1"]
    for button in [button for widget in play_widgets for button in _buttons(widget)]:
        function = functions[_function_id(button)]
        name = function.attrib["Name"].removeprefix("Jugar · ")
        if name in expected:
            actual[name] = (button.attrib["Caption"], find_local(button, "Key").text)
    assert actual == expected


def test_the_play_page_carries_the_exact_operator_guidance(console):
    """2026-09-02: recovery instructions must be readable on the page itself."""
    _, outer = console
    labels = [
        widget.attrib.get("Caption", "")
        for widget, _, _ in _walk(outer)
        if localname(widget) == "Label"
    ]
    assert labels.count("Volver del todo: AUTO dos veces si ya esta verde, o Backspace y Q.") == 1
    assert (
        labels.count(
            "Pick fijo; repetirlo lo para y deja la familia quieta. AUTO colores o "
            "Q/F1-F4 devuelve la rueda; pararla corta su fundido de 800 ms."
        )
        == 1
    )
    assert (
        labels.count(
            "Bajo AUTO, el ciclo de energia lo recupera en su siguiente paso "
            "(8 min como mucho); para jugar largo pon antes un Momento."
        )
        == 3
    )


def test_no_play_pick_is_reachable_from_a_room_state(console):
    """2026-09-02: state starts release picks through hooks, never start the picks."""
    root, outer = console
    functions = _functions_by_id(root)
    ids_by_name = {
        function.attrib["Name"]: function_id for function_id, function in functions.items()
    }
    reachable = set()
    members = _members(root)
    for state_name, _, _, _ in ROOM_STATES:
        state_id = ids_by_name[state_name]
        reachable.add(state_id)
        reachable.update(members.get(state_id, set()))

    hook_names = {
        "Rueda Colores",
        "Rueda Mezcla",
        "Luz Charla",
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
    for caption in ("COLOR", "PIXELES", "CABEZAS", "GOBOS", "PRISMA"):
        family = _frame_named(outer, caption)
        for pick in _buttons(family):
            function_id = _function_id(pick)
            if functions[function_id].attrib["Name"] in hook_names:
                continue
            assert function_id not in reachable, functions[function_id].attrib["Name"]


def test_every_play_pick_is_a_one_member_family_wrapper(console):
    """2026-09-02: picks monitor isolated wrappers, never state-owned leaves."""
    root, outer = console
    functions = _functions_by_id(root)
    hooks_per_family = {
        "COLOR": 3,
        "PIXELES": 2,
        "CABEZAS": 4,
        "GOBOS": 2,
        "PRISMA": 2,
    }
    paths = {
        "COLOR": "Jugar/Color",
        "PIXELES": "Jugar/Pixeles",
        "CABEZAS": "Jugar/Cabezas",
        "GOBOS": "Jugar/Gobos",
        "PRISMA": "Jugar/Prisma",
    }
    for caption, hook_count in hooks_per_family.items():
        picks = _buttons(_frame_named(outer, caption))[hook_count:]
        assert picks
        for pick in picks:
            function = functions[_function_id(pick)]
            assert function.attrib["Type"] == "Collection"
            assert function.attrib["Path"] == paths[caption]
            assert len(findall_local(function, "Step")) == 1


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
        "AUTO colores · W": "Rueda Colores",
        "Mezcla · E": "Rueda Mezcla",
        "AUTO normal · A": "Movimientos Cabezas",
        "AUTO gobos · G": "Gobo Animacion",
        "AUTO prisma · P": "Prisma Animacion",
        "Arcoiris junto · '": "Arcoiris Simultaneo",
        "Arcoiris fases · ¡": "Arcoiris Pasos",
    }
    play_widgets = [child for child in _console_frame(outer) if child.attrib.get("Page") == "1"]
    buttons = [button for widget in play_widgets for button in _buttons(widget)]
    bound = {}
    for button in buttons:
        inputs = [source for source in findall_local(button, "Input") if "Channel" in source.attrib]
        if inputs:
            assert len(inputs) == 1
            bound[button.attrib["Caption"]] = int(inputs[0].attrib["Channel"])
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
    from qlctool.generate.canonical_show import KEYS
    from qlctool.generate.smc_pad_bindings import SMC_PAD_BINDINGS

    root, root_frame = console
    console_frame = _console_frame(root_frame)
    functions = _functions_by_id(root)
    widgets = [widget for widget, _, _ in _walk(root_frame)]

    def named(tag, caption):
        matches = [
            widget
            for widget in widgets
            if localname(widget) == tag and widget.attrib.get("Caption", "").startswith(caption)
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
        ("Button", "HUMO VERTICAL"),
        ("Frame", "Color de los BEAM"),
        ("AudioTriggers", "Audio"),
    )
    retained = {(tag, caption): named(tag, caption) for tag, caption in contracts}

    movement_dial = retained[("SpeedDial", "Vel. Movimiento")]
    dial_inputs = list(findall_local(movement_dial, "Input"))
    assert {source.attrib.get("Key") for source in dial_inputs} >= {"M"}
    assert {
        int(source.attrib["Channel"]) for source in dial_inputs if "Channel" in source.attrib
    } == {SMC_PAD_BINDINGS["Vel. Movimiento"]}

    grand_master = retained[("Slider", "Master General")]
    assert find_local(grand_master, "SliderMode").text == "GrandMaster"
    assert [
        int(source.attrib["Channel"])
        for source in findall_local(grand_master, "Input")
        if "Channel" in source.attrib
    ] == [SMC_PAD_BINDINGS["Master General"]]
    control_labels = {
        widget.attrib.get("Caption", "")
        for widget in widgets
        if localname(widget) == "Label" and _console_page(widget, console_frame) == PAGE_CONTROL
    }
    assert set(GRAND_MASTER_LINES) <= control_labels

    bass = retained[("Button", "GOLPE GRAVES")]
    assert functions[_function_id(bass)].attrib["Name"] == "Golpe Graves"
    assert find_local(bass, "Action").text == "Flash"
    assert not (find_local(bass, "Key").text or "")

    vertical = retained[("Button", "HUMO VERTICAL")]
    assert functions[_function_id(vertical)].attrib["Name"] == "Humo Vertical"
    assert find_local(vertical, "Action").text == "Toggle"
    assert find_local(vertical, "Key").text == KEYS["Humo Vertical"]

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
    guidance = state_for("Label", "Apunta las 12 cabezas")
    pad = state_for("XYPad", "Cabezas")

    def geometry(state):
        return tuple(int(state.attrib[name]) for name in ("X", "Y", "Width", "Height"))

    assert geometry(beam) == (540, 68, 628, 150)
    assert geometry(guidance) == (540, 224, 628, 20)
    assert geometry(pad) == (540, 250, 628, 636)
