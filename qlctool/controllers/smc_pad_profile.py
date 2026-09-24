"""The M-VAVE SMC-PAD as a profile: `smc_pad_bindings`, `smc_pad_colors`, `input_binding`."""

from ..generate.smc_pad_bindings import SMC_PAD_BINDINGS
from ..generate.smc_pad_colors import FUNCTION_COLORS
from ..input_binding import pin_midi_input
from .midi_pad_profile import MidiPadProfile

SMC_PAD = MidiPadProfile(
    name="smc-pad",
    bindings=SMC_PAD_BINDINGS,
    colors=FUNCTION_COLORS,
    pin_input=pin_midi_input,
)
