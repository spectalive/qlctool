"""Every MIDI pad profile the toolkit ships, by the name a description uses."""

from collections.abc import Mapping

from .midi_pad_profile import MidiPadProfile
from .smc_pad_profile import SMC_PAD

MIDI_PADS: Mapping[str, MidiPadProfile] = {SMC_PAD.name: SMC_PAD}
