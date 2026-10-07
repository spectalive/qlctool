"""The SMC-PAD's MIDI channels, note base and the QLC+ omni-mode arithmetic."""

# 1-based, the way both the pad's manual and QLC+'s own UI count MIDI channels.
PAD_MIDI_CHANNEL = 10
CONTROL_MIDI_CHANNEL = 1

# QLC+'s omni-mode input channel arithmetic (plugins/midi/src/common).
OMNI_CHANNEL_SHIFT = 12
NOTE_OFFSET = 128

PADS = 16
FIRST_PAD_NOTE = 36
