"""[controllers]: the MIDI pad profile, the tablet desk and the OSC prefix. Omitted means none."""

from collections.abc import Mapping
from typing import Any

from ...controllers.midi_pads import MIDI_PADS
from ..controller_settings import ControllerSettings
from .reject_unknown_keys import reject_unknown_keys
from .valid_osc_prefix import valid_osc_prefix


def read_controllers(table: Mapping[str, Any], where: str) -> ControllerSettings:
    """The stated controllers; none for an absent table, as the spec says."""
    here = f"{where}: [controllers]"
    reject_unknown_keys(table, ("midi_pad", "tablet_desk", "osc"), here)
    midi_pad = table.get("midi_pad")
    if midi_pad is not None and (not isinstance(midi_pad, str) or midi_pad not in MIDI_PADS):
        raise ValueError(
            f"{here} midi_pad {midi_pad!r} is not a known pad; "
            f"known: {', '.join(sorted(MIDI_PADS))}"
        )
    tablet_desk = table.get("tablet_desk", False)
    if not isinstance(tablet_desk, bool):
        raise ValueError(f"{here} tablet_desk is true or false")
    osc = table.get("osc")
    if osc is not None and not valid_osc_prefix(osc):
        raise ValueError(
            f"{here} osc {osc!r} is an address prefix: a '/' and a name, "
            "no trailing '/' and no spaces, such as \"/desk\""
        )
    return ControllerSettings(midi_pad=midi_pad, tablet_desk=tablet_desk, osc=osc)
