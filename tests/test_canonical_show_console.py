"""The canonical show's console: its keyboard shortcuts and its hardware pad.

Split by topic out of the original `test_canonical_show.py` (over the
codeality test-file line cap).
"""

import pytest
from rig_root import RIG_ROOT

from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.generate.build_canonical_show import build_canonical_show
from qlctool.localname import localname
from qlctool.vibra.keys import KEYS
from qlctool.workspace import Workspace

REPO = RIG_ROOT
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"


def _functions(root):
    return {
        f.attrib["ID"]: f
        for f in find_local(root, "Engine")
        if localname(f) == "Function" and f.attrib.get("ID")
    }


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    ws = Workspace.load(SHOW)
    show = build_canonical_show(ws, FixtureLibrary.load())
    out = tmp_path_factory.mktemp("show") / "Vibra.qxw"
    ws.save(out)
    return show, out


def test_the_console_carries_the_old_keyboard_shortcuts(built):
    show, out = built
    root = Workspace.load(out).root
    buttons = {}
    for element in root.iter():
        if localname(element) != "Button":
            continue
        function = find_local(element, "Function")
        key = find_local(element, "Key")
        if function is not None and key is not None and key.text:
            buttons[int(function.attrib["ID"])] = (key.text, find_local(element, "Action").text)

    assert buttons[show.master_ids["AUTO"]] == ("Q", "Toggle")
    assert buttons[show.master_ids["Flash 100%"]] == ("Space", "Flash")
    assert buttons[show.master_ids["Todo Negro"]] == (KEYS["Todo Negro"], "Toggle")


def test_the_console_is_bound_to_the_smc_pad(built):
    """2026-08-29: the M-VAVE SMC-PAD became the show's hardware surface.

    Every widget the map names carries its <Input> binding (universe 0), and
    every channel appears exactly once - a channel bound twice is one pad
    pressing two widgets at a venue in the dark. Source ID is 0, the primary
    control, everywhere but the multipage frame, whose Previous Page is 1.
    """
    from qlctool.generate.smc_pad_bindings import SMC_PAD_BINDINGS
    from qlctool.names.default_names import default_names

    names = default_names()
    show, out = built
    root = Workspace.load(out).root

    channels = []
    button_channel = {}
    caption_channel = {}
    frame_pages = {}
    for element in root.iter():
        if localname(element) not in ("Button", "Slider", "SpeedDial", "Frame"):
            continue
        for source in findall_local(element, "Input"):
            if "Universe" not in source.attrib:
                # A key-only <Input> (the colour dial's tap on M,
                # 2026-08-29) binds a keyboard key, not a pad channel.
                assert "Key" in source.attrib
                continue
            assert source.attrib["Universe"] == "0"
            channel = int(source.attrib["Channel"])
            channels.append(channel)
            if localname(element) == "Frame":
                frame_pages[source.attrib["ID"]] = channel
                continue
            assert source.attrib["ID"] == "0"
            caption_channel[element.attrib.get("Caption")] = channel
            if localname(element) == "Button":
                function = find_local(element, "Function")
                button_channel[int(function.attrib["ID"])] = channel

    # Every channel at most once, none the map does not name - and a binding
    # may only be missing when its master is: the seed workspace has no
    # vertical smoke machines, so pad 9 has nothing to press there.
    assert len(channels) == len(set(channels))
    assert set(channels) <= set(SMC_PAD_BINDINGS.values())
    inverse = {ch: names.display(name) for name, ch in SMC_PAD_BINDINGS.items()}
    for channel in set(SMC_PAD_BINDINGS.values()) - set(channels):
        assert inverse[channel] not in show.master_ids, inverse[channel]

    # The pads land on the functions the owner put under those fingers...
    for name in ("auto", "flash_full", "smoke_on", "full_white", "colour_wheel"):
        assert button_channel[show.master_ids[names.display(name)]] == SMC_PAD_BINDINGS[name]
    # ...and the encoders on the widgets that scale, not fire.
    for name in ("grand_master", "tempo_dial"):
        assert caption_channel[names.display(name)] == SMC_PAD_BINDINGS[name]
    # The transport buttons: arrows page the console, pause and record are
    # the panic pair - off the pads, where a missed hit cannot reach them.
    assert frame_pages == {
        "0": SMC_PAD_BINDINGS["page_next"],
        "1": SMC_PAD_BINDINGS["page_previous"],
    }
    assert caption_channel["PARAR TODO · Retroceso"] == SMC_PAD_BINDINGS["stop_all"]
    assert caption_channel["APAGON · Esc"] == SMC_PAD_BINDINGS["blackout"]


def test_both_tap_dials_share_one_key_and_scale_by_layer(built):
    """2026-08-29: the owner asked for the movement on the tap too.

    A key press reaches every widget bound to it (VCPage::handleKeyEvent walks
    all matches), so one M taps both dials - the hand-built console's design.
    What each dial must NOT do is give every layer the same multiplier: QLC+
    writes `dial time x multiplier` into each function, so one shared value
    flattens the show to a single length ("se vuelven todos los programas
    locos").
    """
    _, out = built
    root = Workspace.load(out).root

    dials = {d.attrib["Caption"]: d for d in root.iter() if localname(d) == "SpeedDial"}
    assert set(dials) == {"Tempo Show", "Vel. Movimiento"}

    for caption, dial in dials.items():
        taps = [source for source in findall_local(dial, "Input") if source.attrib.get("ID") == "1"]
        assert [t.attrib.get("Key") for t in taps] == ["M"], caption

        multipliers = [int(f.attrib["Duration"]) for f in findall_local(dial, "Function")]
        assert len(multipliers) >= 3, caption
        assert len(set(multipliers)) > 1, f"{caption} re-times every layer to the same length"

    # The movement dial carries the EFX as well as the rotations, and re-times
    # the crossfade too: QLC+ subtracts a chaser's fade from its EFX's own
    # duration to get the figure it draws (EFX::loopDuration), so a fade left
    # at fixed milliseconds stops the figure being a proportion of the step.
    functions = _functions(root)
    movement = {
        functions[f.text].attrib["Name"]: f
        for f in findall_local(dials["Vel. Movimiento"], "Function")
    }
    assert any(functions_by_name(functions, name).attrib["Type"] == "EFX" for name in movement)
    assert int(movement["Movimientos Washes"].attrib["FadeIn"]) > 0


def functions_by_name(functions, name):
    return next(f for f in functions.values() if f.attrib.get("Name") == name)
