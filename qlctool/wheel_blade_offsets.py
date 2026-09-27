"""The blade of a fixture whose colour is a wheel: it opens with the colour.

On an RGB fixture colour and light are one thing: its red, green and blue are
Intensity channels, merged HTP, so when every colour writer stops the fixture
goes dark with the rest of the rig. A wheel is LTP and keeps its last position
whoever stopped, so a head whose only colour is a wheel stays lit in the last
colour for as long as its dimmer is open. The four 7R did exactly that when a
colour pick was released under AUTO: the rig went black and the beams stayed
red, because the level held their blade open (en-sala DMX audit, 2026-09-26,
item 5).

A blade dimmer (`stepped_dimmer_offsets`) has no level to give - open or shut, the
quiet level already wrote it at full - so it carries nothing the level owns.
On a wheel-coloured head it goes with the colour instead: every colour look
that puts the wheel somewhere opens it, the levels leave it alone, and when
the colour writers stop the blade drops with the RGB of the rest of the rig
(ruling D8, 2026-09-27).

What that changes, checked in the round 3 review: after PARAR TODO a colour
pick pressed on its own now opens the beams at full, while the fixtures a
level dims (the MACs) stay dark until a level runs. A crossfade between two
colour looks does not dip the blade - the incoming fade starts from the value
the outgoing step still holds, and HTP keeps the higher - but the first fade
in from dark walks it through its partial range, as it did when the levels
held it.
"""

from . import roles
from .fixture_capabilities import FixtureCapabilities
from .stepped_dimmer_offsets import stepped_dimmer_offsets


def wheel_blade_offsets(capability: FixtureCapabilities) -> list[int]:
    """The blade offsets a wheel colour opens: none unless the colour is only a wheel."""
    if not capability.has_role(roles.COLOR_MACRO) or capability.has_role(roles.RED):
        return []
    return stepped_dimmer_offsets(capability)
