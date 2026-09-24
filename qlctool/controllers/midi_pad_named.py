"""The pad profile a description names, or none."""

from .midi_pad_profile import MidiPadProfile
from .midi_pads import MIDI_PADS


def midi_pad_named(name: str | None) -> MidiPadProfile | None:
    """None for no pad; the profile for a known name; an error listing the known ones otherwise."""
    if name is None:
        return None
    if name not in MIDI_PADS:
        raise ValueError(f"unknown MIDI pad {name!r}; known: {', '.join(sorted(MIDI_PADS))}")
    return MIDI_PADS[name]
