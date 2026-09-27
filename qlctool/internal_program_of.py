"""Resolve a fixture's own-program channels, if it has any."""

from . import roles
from .fixture_capabilities import FixtureCapabilities
from .internal_program import InternalProgram
from .mode_channel import mode_channel


def internal_program(capabilities: FixtureCapabilities) -> InternalProgram | None:
    """Resolve the fixture's own-program channels, or None when it has none.

    Recognised by shape, never by model: one effect channel whose ranges name a
    mode - one of them "no function", another an automatic one - and a second
    effect channel carrying the list of programs to choose from.
    """
    channels = capabilities.capabilities_for_role(roles.EFFECT)
    if len(channels) < 2:
        return None

    mode = mode_channel(channels)
    if mode is None:
        return None
    mode_offset, off_range, auto_range = mode

    effects = max(
        (item for item in channels if item[0] != mode_offset),
        key=lambda item: len(item[1]),
    )
    if len(effects[1]) < 2:
        return None

    speed = capabilities.offsets_for_role(roles.SPEED)
    return InternalProgram(
        mode_offset=mode_offset,
        off_value=off_range.middle,
        auto_value=auto_range.middle,
        effect_offset=effects[0],
        effects=effects[1],
        speed_offset=speed[0] if speed else None,
    )
