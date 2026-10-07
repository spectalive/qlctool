from .smc_pad_constants import (
    FIRST_PAD_NOTE,
    NOTE_OFFSET,
    OMNI_CHANNEL_SHIFT,
    PAD_MIDI_CHANNEL,
    PADS,
)


def pad_channel(pad: int, bank: int = 1) -> int:
    """The QLC+ input channel for physical pad 1-16 on bank 1 or 2."""
    if not 1 <= pad <= PADS:
        raise ValueError(f"pad {pad} is not one of the device's 1-{PADS}")
    if bank not in (1, 2):
        raise ValueError(f"bank {bank}: the show only uses the pad's first two")
    note = FIRST_PAD_NOTE + (bank - 1) * PADS + pad - 1
    return ((PAD_MIDI_CHANNEL - 1) << OMNI_CHANNEL_SHIFT) + NOTE_OFFSET + note
