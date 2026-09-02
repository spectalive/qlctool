"""The channels of a fixture that are wheels, and therefore must never fade.

QLC+ fades every channel a scene writes unless the fixture excludes it
(`Fixture::channelCanFade`, true for anything not in `<ExcludeFade>`), and a
FadeChannel starts from the value the universe currently holds. So the
rig-wide colour wheel's 800 ms crossfade did not only soften the LEDs: on the
four BEAM 230W 7R it walked the mechanical colour wheel from Red (12) to Blue
(43) through orange, yellow and green, twenty-one steps every 3.3 seconds, all
night (cross-audit, 2026-09-02). A wheel is a set of detents; a value between
two of them is half of each.

Which channels are wheels is read off the definition - a colour wheel, a gobo
wheel, a prism - by role, never by model. The continuous half-colour channel
beside the wheel counts too: it is the same motor.
"""

from . import roles
from .capability import FixtureCapabilities

WHEEL_ROLES = (roles.COLOR_MACRO, roles.GOBO, roles.PRISM)


def wheel_fade_offsets(capabilities: FixtureCapabilities) -> list[int]:
    """Offsets QLC+ must snap rather than fade on this fixture, in order."""
    return sorted(
        offset for role in WHEEL_ROLES for offset in capabilities.offsets_for_role(role)
    )
