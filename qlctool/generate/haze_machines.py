"""The fog-only machines: the haze a timer may fire, never a lit column.

A smoke machine that also carries lights is a show machine - a vertical
column somebody fires on purpose - and a timer that fires it all night is a
wrong show and an empty tank. `smoke_auto` and `newshow` both ask this.
"""

from collections.abc import Iterable

from .. import roles
from ..capability import FixtureCapabilities


def haze_machines(capabilities: Iterable[FixtureCapabilities]) -> list[FixtureCapabilities]:
    """Every smoke machine without a red channel, in patch order."""
    return [c for c in capabilities if c.is_smoke and not c.has_role(roles.RED)]
