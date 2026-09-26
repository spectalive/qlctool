"""The M-VAVE SMC-PAD's map: which physical control fires which console widget.

The numbers come from `smc_pad_device`, which holds what the pad measurably
sends; this file only says what each control is *for*. Keys are catalogue
identifiers: a master function's for buttons, the `[console]` caption's for the
sliders, dials and small buttons. `build_canonical_show` localises them to the
widget's identity in `generate_live_console` (`localised_keys`).

The layout is the owner's (2026-08-29): hits on the top two rows - the first
column is the build-up punch (flash + vertical smoke), the second the gentler
fills (slow flash + plain smoke) - room states on the two bottom rows, and the
panic stays OFF the pads so a missed hit cannot black the room out. Pad 4
(bottom-right) is left free on purpose for the same reason.

The manual layer moved to the pad's **second bank** on 2026-08-29. It was
written against SHIFT, and a capture that night proved SHIFT sends no MIDI at
all - it picks the functions silkscreened on the pads (SWING, LATCH, SYNC),
which never leave the device. Those eight bindings had therefore never fired.
PAD BANK does leave the device: it moves every pad up 16 notes, so the manual
layer now sits on the same physical pads as the hits, one bank up.

The five small buttons on the right edge: `<` CC 25, `>` CC 26, play CC 27,
stop CC 28 (the manual's STOP, which the show calls Pausa), record CC 29. The
arrows page the console like PgUp/PgDown - and they were measured not to change
the pad's bank, so paging cannot silently move the hits. Pausa is PARAR TODO
and record is APAGON, the panic pair, physically apart from the pads and on a
control change, so they answer on either bank.
Play stays free: a button can carry one external source per control, and AUTO's
is pad 5's.
"""

from .smc_pad_device import control_channel, pad_channel

SMC_PAD_BINDINGS: dict[str, int] = {
    # Bank 1, top row (pads 13-16): the hits you hammer.
    "flash_full": pad_channel(13),  # the punch
    "flash_half": pad_channel(14),  # the gentler fill
    "flash_colour": pad_channel(15),
    # Bank 1, second row (pads 9-12): smoke and strobes.
    "vertical_smoke_now": pad_channel(9),  # the punch, under pad 13
    "smoke_on": pad_channel(10),  # the fill, under pad 14
    "strobe_fast": pad_channel(11),
    "strobe_medium": pad_channel(12),
    # Bank 1, third row (pads 5-8): the room's states.
    "auto": pad_channel(5),
    "party_moment": pad_channel(6),
    "frenzy_moment": pad_channel(7),
    "calm_moment": pad_channel(8),
    # Bank 1, bottom row (pads 1-3); pad 4 stays free.
    "full_white": pad_channel(1),
    "all_black": pad_channel(2),
    "talk_moment": pad_channel(3),
    # Bank 2 (PAD BANK), top two rows: the manual layers, on the same fingers
    # as the hits they replace.
    "colour_wheel": pad_channel(13, bank=2),
    "mix_wheel": pad_channel(14, bank=2),
    "head_movements": pad_channel(15, bank=2),
    "gobo_animation": pad_channel(16, bank=2),
    "prism_animation": pad_channel(9, bank=2),
    "smoke_auto": pad_channel(10, bank=2),
    "rainbow_together": pad_channel(11, bank=2),
    "rainbow_steps": pad_channel(12, bank=2),
    # Encoders (CC on channel 1, absolute 0-127). The device numbers its knobs
    # bottom-up too: knob 1 is bottom-left, labeled RATE on the panel.
    "grand_master": control_channel(30),  # the whole room's intensity
    "tempo_dial": control_channel(31),  # the tap dial's time wheel
    "movement_speed": control_channel(32),  # the movement dial's
    # The small buttons on the right edge (CC on channel 1, 127/0).
    "page_previous": control_channel(25),  # "<" - the console's PgUp
    "page_next": control_channel(26),  # ">" - the console's PgDown
    "stop_all": control_channel(28),  # STOP (the show's Pausa) - stop every running function
    "blackout": control_channel(29),  # record - the blackout latch
}
