"""The QLC+ input channel for a knob or button's control change, on the SMC-PAD."""

from .smc_pad_device import CONTROL_MIDI_CHANNEL, OMNI_CHANNEL_SHIFT


def control_channel(cc: int) -> int:
    if not 0 <= cc <= 127:
        raise ValueError(f"CC {cc} is outside MIDI's 0-127")
    return ((CONTROL_MIDI_CHANNEL - 1) << OMNI_CHANNEL_SHIFT) + cc
