"""The M-VAVE SMC-PAD's map: which physical control fires which console widget.

Captured from the real device over USB on 2026-08-29 (port "SINCO
SMC-PAD-Master"). The pad numbers below follow the device's own convention -
pad 1 is bottom-left, pad 13 top-left, like a Launchpad - which is how the
owner names them. The capture proved the TOP-left pad sends the LOWEST note:
top row notes 4-7, then 8-11, 12-15, and the bottom row 16-19. Holding SHIFT
moves every pad up 48 notes (52-67). Pads speak on MIDI channel 10, the
encoders and the five small buttons on channel 1 (encoders CC 30-37 absolute,
buttons CC 25-29).

The QLC+ MIDI input must therefore run in omni ("1-16") mode, and in omni
QLC+ ORs the 0-based MIDI channel into bits 12+ of the input channel number
(plugins/midi/src/common/midiprotocol.cpp): a pad's channel is
9*4096 + 128 + note, an encoder's is just its CC number.

The layout is the owner's (2026-08-29): hits on the top two rows - the first
column is the build-up punch (flash + vertical smoke), the second the gentler
fills (slow flash + plain smoke) - room states on the two bottom rows, and
the panic stays OFF the pads so a missed hit cannot black the room out.
Pad 4 (bottom-right) is left free on purpose for the same reason. The five
small buttons wait for a photo of their icons before they get jobs.

Keys are the widget's identity in `generate_live_console`: a master function's
name for buttons, the widget caption for the sliders and dials.
"""

SMC_PAD_BINDINGS: dict[str, int] = {
    # Top row, pads 13-16 (notes 4-7): the hits you hammer.
    "Flash 100%": 36996,           # pad 13 - the punch
    "Flash 50%": 36997,            # pad 14 - the gentler fill
    "Flash Color": 36998,          # pad 15
    "Color Beam Animacion": 36999, # pad 16
    # Second row, pads 9-12 (notes 8-11): smoke and strobes.
    "Humo Vertical YA": 37000,     # pad 9 - the punch, under pad 13
    "Humo ON": 37001,              # pad 10 - the fill, under pad 14
    "Strobo Rapido": 37002,        # pad 11
    "Strobo Medio": 37003,         # pad 12
    # Third row, pads 5-8 (notes 12-15): the room's states.
    "AUTO": 37004,                 # pad 5
    "Momento Fiesta": 37005,       # pad 6
    "Momento Locura": 37006,       # pad 7
    "Momento Tranquilo": 37007,    # pad 8
    # Bottom row, pads 1-3 (notes 16-18); pad 4 (note 19) stays free.
    "Blanco Total": 37008,         # pad 1
    "Todo Negro": 37009,           # pad 2
    "Momento Charla": 37010,       # pad 3
    # SHIFT + top two rows (notes 52-59): the manual layers.
    "Rueda Colores": 37044,        # shift + pad 13
    "Rueda Mezcla": 37045,         # shift + pad 14
    "Movimientos Cabezas": 37046,  # shift + pad 15
    "Gobo Animacion": 37047,       # shift + pad 16
    "Prisma Animacion": 37048,     # shift + pad 9
    "Humo Auto": 37049,            # shift + pad 10
    "Arcoiris Simultaneo": 37050,  # shift + pad 11
    "Arcoiris Pasos": 37051,       # shift + pad 12
    # Encoders (CC on channel 1, absolute 0-127).
    "Master General": 30,          # encoder 1 - the whole room's intensity
    "Vel. Colores": 31,            # encoder 2
    "Vel. Movimiento": 32,         # encoder 3
}
