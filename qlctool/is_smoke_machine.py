"""Whether a patched fixture makes smoke or haze: what a caption saying "haze" needs.

A fixture QLC+ types as Smoke or Hazer, or one with a pump channel (the
`smoke` role, which reads fog, smoke, humo, haze and hazer). Page 3's title
said "y humo" on a rig with panels and no smoke machine, because the
generator promised haze from the panels' light cue for the column alone
(2026-09-25, review of `rotulo que promete lo que no hay`). The generator's
title and the rule both ask this now.
"""

from . import roles
from .capability import FixtureCapabilities

SMOKE_TYPES = ("smoke", "hazer")


def is_smoke_machine(capabilities: FixtureCapabilities) -> bool:
    return capabilities.fixture_type.lower() in SMOKE_TYPES or capabilities.has_role(roles.SMOKE)
