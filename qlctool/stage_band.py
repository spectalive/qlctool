"""Decide which band of the stage a fixture belongs on.

The 2D and 3D views read one position per fixture out of `<Monitor>`, and a show
that never had those written puts every fixture on top of the next. Placing them
needs a rule, and the rule here is the same one the rest of the toolkit uses:
what the fixture *can do*, not what it is called. A mover with a gobo wheel is a
beam and hangs upstage; a mover without one is a wash and hangs downstage;
anything that only makes colour stands on the floor at the front; a bar lies on
the floor at the back; a smoke machine goes in a corner where nobody walks.
"""

from . import roles
from .capability import FixtureCapabilities

BEAMS = "beams"
WASHES = "washes"
PARS = "pars"
BARS = "bars"
SMOKE = "smoke"

# Upstage to downstage, which is also the order the rows are laid out in.
BANDS = (BEAMS, WASHES, BARS, PARS, SMOKE)


def band_of(capabilities: FixtureCapabilities) -> str:
    if capabilities.is_smoke:
        return SMOKE
    if capabilities.fixture_type.lower().startswith("led bar"):
        return BARS
    if capabilities.has_role(roles.PAN) and capabilities.has_role(roles.TILT):
        return BEAMS if capabilities.has_role(roles.GOBO) else WASHES
    return PARS
