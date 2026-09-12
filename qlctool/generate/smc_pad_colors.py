"""The colour each SMC-PAD function wears - on the pad's LED and on its console
button, so the two read as the same surface.

One RGB per master function. The live console paints the button this colour; the
LED bridge (`tools/smc-pad/qlc_led_bridge.swift`) paints the pad the same colour,
dimmed while the function is idle and full-bright while it is active. Keep the
two palettes in step: the bridge hard-codes the matching values by physical pad.

Physical pad layout the colours follow (bank 1, as the owner arranged it):

    13 Flash    14 Flash50   15 FlashCol  16 ColorBeam
     9 HumoVert 10 Humo      11 Strobo    12 StroboMed
     5 AUTO      6 Fiesta     7 Locura     8 Tranquilo
     1 Blanco    2 Negro      3 Charla     4 (free)

And bank 2 (PAD BANK), carrying the JUGAR/page-2 hooks because SHIFT sends no
MIDI at all:

    13 RuedaCol 14 RuedaMez  15 Movim     16 Gobo
     9 Prisma   10 HumoAuto  11 ArcoSim   12 ArcoPasos
"""

RGB = tuple[int, int, int]

FUNCTION_COLORS: dict[str, RGB] = {
    # Bottom row: base states.
    "Blanco Total": (255, 255, 255),  # pad 1  - work light, white
    "Todo Negro": (255, 40, 40),  # pad 2  - kill, red
    "Momento Charla": (255, 170, 60),  # pad 3  - talk, warm amber
    # Third row: the room's moods.
    "AUTO": (40, 255, 60),  # pad 5  - the go state, green
    "Momento Fiesta": (255, 40, 180),  # pad 6  - party, magenta
    "Momento Locura": (255, 90, 0),  # pad 7  - peak, orange
    "Momento Tranquilo": (40, 120, 255),  # pad 8  - lull, blue
    # Second row: smoke and strobes.
    "Humo Vertical YA": (0, 220, 255),  # pad 9  - cyan
    "Humo ON": (150, 220, 255),  # pad 10 - pale cyan
    "Strobo Rapido": (255, 255, 0),  # pad 11 - yellow
    "Strobo Medio": (255, 200, 0),  # pad 12 - amber
    # Top row: the flash hits.
    "Flash 100%": (255, 255, 255),  # pad 13 - white
    "Flash 50%": (255, 225, 180),  # pad 14 - warm white
    "Flash Color": (255, 0, 255),  # pad 15 - magenta
    "Color Beam Animacion": (0, 255, 255),  # pad 16 - cyan
    # Bank 2, second row: the effects you layer by hand.
    "Prisma Animacion": (255, 255, 255),  # pad 9  - white
    "Humo Auto": (150, 220, 255),  # pad 10 - pale cyan, the smoke family
    "Arcoiris Simultaneo": (255, 140, 0),  # pad 11 - orange
    "Arcoiris Pasos": (255, 220, 0),  # pad 12 - yellow
    # Bank 2, top row: the wheels and the movement.
    "Rueda Colores": (255, 0, 128),  # pad 13 - pink
    "Rueda Mezcla": (128, 0, 255),  # pad 14 - violet
    "Movimientos Cabezas": (0, 128, 255),  # pad 15 - blue
    "Gobo Animacion": (0, 255, 128),  # pad 16 - spring green
}


def readable_foreground(rgb: RGB) -> RGB:
    """Black on a light colour, white on a dark one - so the caption survives."""
    r, g, b = rgb
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return (0, 0, 0) if luminance > 150 else (255, 255, 255)
