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
from qlctool.generate.live_console import CANVAS_HEIGHT, CANVAS_WIDTH
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
    assert pages == 2  # the mixes and the matrices


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


def test_the_audio_bands_press_toggle_buttons_that_exist(console):
    """A bar presses on the way up and again on the way down, so its target
    has to be a Toggle button - a Flash one would latch and never release."""
    _, frame = console
    buttons = {
        int(w.attrib["ID"]): w
        for w, _, _ in _walk(frame)
        if localname(w) == "Button"
    }
    triggers = [w for w, _, _ in _walk(frame) if localname(w) == "AudioTriggers"]
    assert len(triggers) == 1

    bars = findall_local(triggers[0], "SpectrumBar")
    assert bars, "no band is bound to anything"
    for bar in bars:
        assert bar.attrib["Type"] == "3"  # AudioBar::VCWidgetBar
        target = buttons[int(bar.attrib["WidgetID"])]
        assert find_local(target, "Action").text == "Toggle", bar.attrib["Name"]
