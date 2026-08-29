"""Dimmer channels that are not faders, and must only ever be set to an end.

Most dimmers here are a plain fader: the definition declares
`<Channel Name="Dimmer" Preset="IntensityDimmer"/>` and any value between 0 and
255 is a legitimate brightness. The BEAM 230W 7R's is a mechanical blade that
crosses the aperture from one side, so a value in between does not dim the beam,
it *covers part of the lens*: "las 7R no se abren del todo, están como una media
luna ... el canal 7 de cada 7R está a la mitad en vez de abierto del todo"
(owner, live, 2026-08-29, reading the DMX off the desk). `Intensidad Ambiente`
wrote 110 to every dimmer in the rig, held it for the four minutes of the quiet
level, and that is where the crescent came from.

The difference is read off the definition, not off the model: a dimmer whose
channel carries **labelled ranges** is one whose author had to describe it in
steps, and a channel described in steps is not one a generator may set to a
fraction. A plain fader carries no ranges at all, so nothing else in this rig
is caught by it.
"""

from . import roles
from .capability import FixtureCapabilities


def stepped_dimmer_offsets(capability: FixtureCapabilities) -> list[int]:
    """Offsets of this fixture's dimmer channels that are not smooth faders."""
    return [
        offset
        for offset, ranges in capability.capabilities_for_role(roles.DIMMER)
        if len(ranges) > 1
    ]
