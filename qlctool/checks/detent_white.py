"""Whether a scene parks a wheel-coloured fixture on a detent whose name says white."""

from collections.abc import Mapping

from .. import roles
from ..capability import FixtureCapabilities
from ..color_wheel_match import WHEEL_NAMES

WHITE_DETENTS = tuple(name.lower() for name in WHEEL_NAMES["white"])


def detent_white(capability: FixtureCapabilities, written: Mapping[int, int | None]) -> bool:
    if any(capability.has_role(role) for role in (roles.RED, roles.GREEN, roles.BLUE)):
        return False
    wheel = capability.wheel_for_role(roles.COLOR_MACRO)
    if wheel is None:
        return False
    offset, positions = wheel
    value = written.get(offset)
    if value is None:
        return False
    for position in positions:
        if (position.name or "").strip().lower() not in WHITE_DETENTS:
            continue
        if position.minimum <= value <= position.maximum:
            return True
    return False
