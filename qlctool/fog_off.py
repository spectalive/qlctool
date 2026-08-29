"""The value that shuts a pump, for the scenes that own the room.

The pump is LTP like every other channel, and a Flash writes its value while
held and restores nothing on release: QLC+ takes the flash's own fader away and
whatever is running underneath writes the channel again - if anything does. On
the strobe channels that gap cost a night of flashing panels
(`rule_strobe_restore`). On a pump it costs the tank: "le doy y nunca se para,
se supone que solo debe tirar cuando le de" (owner, live, 2026-08-29, on the
four vertical LED fog machines).

So the scenes that own the room's intensity own the pump too, at zero. They are
already the thing that runs under every flash, and a pump held at zero by a
running scene is a pump that stops the instant the finger leaves the button.
Writing zero is not "touching the smoke" in the sense `rule_smoke` guards: that
rule is about a scene that *fires* the pump beside other fixtures.
"""

from .capability import FixtureCapabilities
from .fog_offsets import fog_offsets


def fog_off_pairs(capabilities: FixtureCapabilities) -> list[tuple[int, int]]:
    """(offset, 0) for every pump channel this fixture has."""
    if not capabilities.is_smoke:
        return []
    return [(offset, 0) for offset in fog_offsets(capabilities)]
