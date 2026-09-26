"""The MIDI note a physical SMC-PAD pad sends, measured on the rig (`smc_pad_device`)."""

from .smc_pad_device import FIRST_PAD_NOTE, PADS


def pad_note(pad: int, bank: int = 1) -> int:
    """Pad 1-16 on bank 1 or 2: 36 is bank 1's bottom-left, and a bank is 16 notes up."""
    return FIRST_PAD_NOTE + (bank - 1) * PADS + pad - 1
