"""The console the show is run from: one screen, and no frame that kills itself.

Two things are checked here that a workspace loading cleanly in QLC+ will not
catch. First that everything fits a 13" laptop, because a console taller than
the screen is unusable at a venue. Second the solo-frame rule: a solo frame
stops every other widget's function the moment one starts, so a function and
anything it starts must never share one - that is what made AUTO die the
instant it was pressed.

Split by topic out of the original `test_live_console.py` (over the codeality
test-file line cap).
"""

import pytest
from members_of_functions import members_of as _members
from rig_root import RIG_ROOT
from walk_widgets import walk_widgets as _walk

from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.generate.build_canonical_show import build_canonical_show
from qlctool.generate.console_layout import CANVAS_HEIGHT, CANVAS_WIDTH
from qlctool.localname import localname
from qlctool.vibra.keys import KEYS
from qlctool.workspace import Workspace

REPO = RIG_ROOT
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"

# Buttons that exist only when the rig has the fixture behind them. The test
# rig is the hand-built DeluxeEventos2, which has no lit fog machine, so its
# console builds without the vertical burst - and, since 2026-09-25, without
# the column's light (`vertical_smoke_columns`).
OPTIONAL_KEYS = {"Humo Vertical YA", "Humo Vertical"}

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
