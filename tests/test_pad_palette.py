"""The pad's LEDs and the console's buttons wear one palette, or they lie.

The point of colouring both is that the surface reads the same whether the
operator looks at the laptop or at their hand. The two live in different
languages - `smc_pad_colors.py` paints the console, `qlc_led_bridge.swift`
paints the pad - and a docstring asking a human to keep them in step is exactly
the arrangement that let the input profile rot. So this reads the bridge's own
array and compares it against the generator's, pad by pad.
"""

import re
from pathlib import Path

from qlctool.generate.smc_pad_bindings import SMC_PAD_BINDINGS
from qlctool.generate.smc_pad_colors import FUNCTION_COLORS
from qlctool.generate.smc_pad_device import (
    FIRST_PAD_NOTE,
    NOTE_OFFSET,
    OMNI_CHANNEL_SHIFT,
    PAD_MIDI_CHANNEL,
    PADS,
)

BRIDGE = Path(__file__).resolve().parents[3] / "tools" / "smc-pad" / "qlc_led_bridge.swift"
FREE_PAD = (20, 20, 20)
ENTRY = re.compile(r"\(\s*(\d+),\s*(\d+),\s*(\d+)\s*\)")


def _bridge_palette(name: str) -> list[tuple[int, int, int]]:
    """The RGB triples of one `let <name>: [(UInt8, UInt8, UInt8)] = [...]`."""
    source = BRIDGE.read_text()
    start = source.index(f"let {name}:")
    body = source[source.index("[", start) + 1 : source.index("\n]", start)]
    colours = []
    for line in body.splitlines():
        line = line.split("//")[0]
        for match in ENTRY.finditer(line):
            colours.append(tuple(int(g) for g in match.groups()))
        colours += [FREE_PAD] * line.count("FREE_PAD")
    return colours


def _pad_of(channel: int) -> tuple[int, int] | None:
    """(bank, pad) for an input channel, or None if it is not a pad."""
    note = channel - (((PAD_MIDI_CHANNEL - 1) << OMNI_CHANNEL_SHIFT) + NOTE_OFFSET)
    offset = note - FIRST_PAD_NOTE
    if not 0 <= offset < 2 * PADS:
        return None
    return offset // PADS + 1, offset % PADS + 1


def test_the_bridge_paints_what_the_console_paints():
    palettes = {1: _bridge_palette("PAD_COLORS"), 2: _bridge_palette("BANK2_COLORS")}
    assert [len(p) for p in palettes.values()] == [PADS, PADS]

    checked = 0
    for name, colour in FUNCTION_COLORS.items():
        channel = SMC_PAD_BINDINGS.get(name)
        assert channel is not None, f"{name} has a colour and no control"
        position = _pad_of(channel)
        assert position is not None, f"{name} is coloured but not on a pad"
        bank, pad = position
        assert palettes[bank][pad - 1] == colour, (
            f"{name}: console paints {colour}, the bridge paints "
            f"{palettes[bank][pad - 1]} on bank {bank} pad {pad}"
        )
        checked += 1
    assert checked == len(FUNCTION_COLORS)


def test_the_pads_with_no_function_stay_dark():
    """A lit pad that does nothing is a pad somebody will press."""
    coloured = {
        _pad_of(SMC_PAD_BINDINGS[name])
        for name in FUNCTION_COLORS
        if _pad_of(SMC_PAD_BINDINGS[name])
    }
    palettes = {1: _bridge_palette("PAD_COLORS"), 2: _bridge_palette("BANK2_COLORS")}
    for bank, palette in palettes.items():
        for pad in range(1, PADS + 1):
            if (bank, pad) not in coloured:
                assert palette[pad - 1] == FREE_PAD, (
                    f"bank {bank} pad {pad} glows {palette[pad - 1]} and no function is bound to it"
                )
