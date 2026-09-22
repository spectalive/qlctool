"""Whether a scene writes a fixture white: red, green and blue all written, all equal, all lit."""

from .. import roles
from ..capability import FixtureCapabilities


def rgb_white(capability: FixtureCapabilities, written: dict[int, int | None]) -> bool:
    stated: list[int] = []
    for role in (roles.RED, roles.GREEN, roles.BLUE):
        values = [
            value
            for offset in capability.offsets_for_role(role)
            if (value := written.get(offset)) is not None
        ]
        if not values:
            return False
        stated.append(max(values))
    return len(set(stated)) == 1 and stated[0] > 0
