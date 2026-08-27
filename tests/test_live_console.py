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
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    HITS,
    ROOM_STATES,
)
from qlctool.library import FixtureLibrary
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, localname

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"

WIDGET_TAGS = {
    "Frame", "SoloFrame", "Button", "Label", "Slider", "XYPad", "SpeedDial",
    "AudioTriggers", "Matrix", "Clock",
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
            int(find_local(b, "Function").attrib["ID"])
            for b in widget
            if localname(b) == "Button"
        }
        for function_id in inside:
            clash = inside & members.get(function_id, set())
            assert not clash, (widget.attrib.get("Caption"), function_id, clash)


def test_every_function_gets_at_most_one_button(console):
    _, frame = console
    driven = [
        int(find_local(b, "Function").attrib["ID"])
        for b, _, _ in _walk(frame)
        if localname(b) == "Button"
    ]
    assert len(driven) == len(set(driven))


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
    assert pages == 3  # the console itself, the mixes and the matrices


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
        assert key in by_key, name
    # 1-0 light the same colour on all three banks, as the old console does.
    assert len(by_key["1"]) == 3
    # Everything else is one key, one look: every widget sees every key
    # press, so two buttons sharing a letter would fire both.
    for key, captions in by_key.items():
        if key in "1234567890":
            continue
        assert len(captions) == 1, (key, captions)


def test_the_audio_bands_ship_unbound_and_never_reach_a_strobe(console):
    """The widget is there for the venue to wire; no band ships bound.

    Until 2026-08-27 the upper mids pressed `Strobo Rapido`: a strobe fired by
    whatever the PA does is a strobe nobody chose, and the flash-rate cap
    means nothing if a cymbal can hold the button. Binding a band is a
    decision to make with the real music playing - and any bar that is bound
    must press a Toggle button (a bar presses on the way up and again on the
    way down, so a Flash target would latch), never a strobe.
    """
    _, frame = console
    buttons = {
        int(w.attrib["ID"]): w
        for w, _, _ in _walk(frame)
        if localname(w) == "Button"
    }
    triggers = [w for w, _, _ in _walk(frame) if localname(w) == "AudioTriggers"]
    assert len(triggers) == 1

    for bar in findall_local(triggers[0], "SpectrumBar"):
        assert bar.attrib["Type"] == "3"  # AudioBar::VCWidgetBar
        target = buttons[int(bar.attrib["WidgetID"])]
        assert find_local(target, "Action").text == "Toggle", bar.attrib["Name"]
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
    return [
        child.attrib.get("Caption", "")
        for child in widget
        if localname(child) == "Button"
    ]


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
    assert len(buttons) == 1
    action = find_local(buttons[0], "Action")
    assert action.text == "StopAll"
    assert int(action.attrib["FadeOut"]) > 0
    # Function::invalidId(): it stops what is running rather than adding to it.
    assert find_local(buttons[0], "Function").attrib["ID"] == "4294967295"


def test_every_button_on_the_show_page_says_its_own_key(console):
    """Nobody reads a key map at a venue: the key is on the button."""
    _, frame = console
    for caption in _captions(_frame_named(frame, "LA SALA ESTÁ ASÍ")) + _captions(
        _frame_named(frame, "GOLPES")
    ):
        assert " · " in caption, caption
    assert [caption for _, caption in HITS] == _captions(_frame_named(frame, "GOLPES"))


def test_a_colour_button_says_which_colour_it_is(console):
    """Thirty blank squares is what the three colour banks used to be."""
    _, frame = console
    for group in ("BarrasLed", "Cabezas", "PAR"):
        bank = _frame_named(frame, f"Colores {group}")
        captions = _captions(bank)
        assert len(captions) == 10
        assert all(captions), group
        assert len(set(captions)) == 10, group


def test_a_mix_button_is_not_ambiguous(console):
    """Azul and Amarillo both start with an A: one letter labelled six pairs
    of different buttons identically."""
    _, frame = console
    mixes = _frame_named(frame, "Mezclas de dos colores")
    by_page = {}
    for child in mixes:
        if localname(child) != "Button":
            continue
        by_page.setdefault(child.attrib.get("Page", "0"), []).append(
            child.attrib["Caption"]
        )
    assert by_page
    for page, captions in by_page.items():
        assert len(captions) == len(set(captions)), page
