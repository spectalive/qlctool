"""The console's room state: exactly one state solo frame, and no way around it.

Split by topic out of the original `test_live_console.py` (over the codeality
test-file line cap).
"""

import pytest
from captions_of import captions_of as _captions
from frame_named import frame_named as _frame_named
from rig_root import RIG_ROOT
from walk_widgets import walk_widgets as _walk

from qlctool.find_local import find_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.generate.build_canonical_show import build_canonical_show
from qlctool.generate.console_layout import HITS, ROOM_STATES
from qlctool.glyph import glyph
from qlctool.leading_glyph import leading_glyph
from qlctool.localname import localname
from qlctool.names.default_names import default_names
from qlctool.workspace import Workspace

REPO = RIG_ROOT
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"

# Buttons that exist only when the rig has the fixture behind them. The test
# rig is the hand-built DeluxeEventos2, which has no lit fog machine, so its
# console builds without the vertical burst - and, since 2026-09-25, without
# the column's light (`vertical_smoke_columns`).
OPTIONAL_KEYS = {"Humo Vertical YA", "Humo Vertical"}


@pytest.fixture(scope="module")
def console(tmp_path_factory):
    ws = Workspace.load(SHOW)
    build_canonical_show(ws, FixtureLibrary.load())
    out = tmp_path_factory.mktemp("console") / "Vibra.qxw"
    ws.save(out)
    root = Workspace.load(out).root
    return root, find_local(find_local(root, "VirtualConsole"), "Frame")


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
    # Each state wears its glyph since 2026-09-22 ("ni un solo icono en los
    # botones", owner): the caption after it is still the show's own.
    names = default_names()
    assert [leading_glyph(c)[1] for c in _captions(room)] == [
        names.display(caption) for _, caption, _, _ in ROOM_STATES
    ]
    assert [leading_glyph(c)[0] for c in _captions(room)] == [
        glyph(identifier) for identifier, _, _, _ in ROOM_STATES
    ]


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
    actual = [leading_glyph(c)[1] for c in _captions(_frame_named(frame, "GOLPES"))]
    names = default_names()
    hits = [(names.display(name), names.display(caption)) for name, caption in HITS]
    expected = [caption for name, caption in hits if name not in OPTIONAL_KEYS or caption in actual]
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
    from qlctool.vc.bank_pitch_for import (
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
