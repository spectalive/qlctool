"""[controllers]: the MIDI pad profile and the tablet desk. Omitted means neither."""

from collections.abc import Mapping
from typing import Any

from ...controllers.midi_pads import MIDI_PADS
from ..controller_settings import ControllerSettings
from .reject_unknown_keys import reject_unknown_keys


def read_controllers(table: Mapping[str, Any], where: str) -> ControllerSettings:
    """The stated controllers; none for an absent table, as the spec says."""
    here = f"{where}: [controllers]"
    reject_unknown_keys(table, ("midi_pad", "tablet_desk"), here)
    midi_pad = table.get("midi_pad")
    if midi_pad is not None and (not isinstance(midi_pad, str) or midi_pad not in MIDI_PADS):
        raise ValueError(
            f"{here} midi_pad {midi_pad!r} is not a known pad; "
            f"known: {', '.join(sorted(MIDI_PADS))}"
        )
    tablet_desk = table.get("tablet_desk", False)
    if not isinstance(tablet_desk, bool):
        raise ValueError(f"{here} tablet_desk is true or false")
    return ControllerSettings(midi_pad=midi_pad, tablet_desk=tablet_desk)
