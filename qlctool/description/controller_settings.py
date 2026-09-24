"""Which control surfaces a show is bound to."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ControllerSettings:
    """A MIDI pad profile name and whether the tablet desk exists. Neither, unless a show says so."""

    midi_pad: str | None = None
    tablet_desk: bool = False
