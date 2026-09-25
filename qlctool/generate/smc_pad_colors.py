"""The colour each SMC-PAD function wears - on the pad's LED and on its console
button, so the two read as the same surface.

One RGB per master function, keyed by its catalogue identifier. The live
console paints the button this colour; the LED bridge
(`tools/smc-pad/qlc_led_bridge.swift`) paints the pad the same colour, dimmed
while the function is idle and full-bright while it is active. Keep the two
palettes in step: the bridge hard-codes the matching values by physical pad.

Physical pad layout the colours follow (bank 1, as the owner arranged it):

    13 Flash    14 Flash50   15 FlashCol  16 (free)
     9 HumoVert 10 Humo      11 Strobo    12 StroboMed
     5 AUTO      6 Fiesta     7 Locura     8 Tranquilo
     1 Blanco    2 Negro      3 Charla     4 (free)

Pad 16 went free on 2026-09-22 with COLOR BEAM, the button that looked like an
on/off and actually stepped the beams' colour wheel.

And bank 2 (PAD BANK), carrying the JUGAR/page-2 hooks because SHIFT sends no
MIDI at all:

    13 RuedaCol 14 RuedaMez  15 Movim     16 Gobo
     9 Prisma   10 HumoAuto  11 ArcoSim   12 ArcoPasos
"""

RGB = tuple[int, int, int]

FUNCTION_COLORS: dict[str, RGB] = {
    # Bottom row: base states.
    "full_white": (255, 255, 255),  # pad 1  - work light, white
    "all_black": (255, 40, 40),  # pad 2  - kill, red
    "talk_moment": (255, 170, 60),  # pad 3  - talk, warm amber
    # Third row: the room's moods.
    "auto": (40, 255, 60),  # pad 5  - the go state, green
    "party_moment": (255, 40, 180),  # pad 6  - party, magenta
    "frenzy_moment": (255, 90, 0),  # pad 7  - peak, orange
    "calm_moment": (40, 120, 255),  # pad 8  - lull, blue
    # Second row: smoke and strobes.
    "vertical_smoke_now": (0, 220, 255),  # pad 9  - cyan
    "smoke_on": (150, 220, 255),  # pad 10 - pale cyan
    "strobe_fast": (255, 255, 0),  # pad 11 - yellow
    "strobe_medium": (255, 200, 0),  # pad 12 - amber
    # Top row: the flash hits.
    "flash_full": (255, 255, 255),  # pad 13 - white
    "flash_half": (255, 225, 180),  # pad 14 - warm white
    "flash_colour": (255, 0, 255),  # pad 15 - magenta
    # Bank 2, second row: the effects you layer by hand.
    "prism_animation": (255, 255, 255),  # pad 9  - white
    "smoke_auto": (150, 220, 255),  # pad 10 - pale cyan, the smoke family
    "rainbow_together": (255, 140, 0),  # pad 11 - orange
    "rainbow_steps": (255, 220, 0),  # pad 12 - yellow
    # Bank 2, top row: the wheels and the movement.
    "colour_wheel": (255, 0, 128),  # pad 13 - pink
    "mix_wheel": (128, 0, 255),  # pad 14 - violet
    "head_movements": (0, 128, 255),  # pad 15 - blue
    "gobo_animation": (0, 255, 128),  # pad 16 - spring green
}


def readable_foreground(rgb: RGB) -> RGB:
    """Black on a light colour, white on a dark one - so the caption survives."""
    r, g, b = rgb
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return (0, 0, 0) if luminance > 150 else (255, 255, 255)
