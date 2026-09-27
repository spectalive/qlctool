"""Whether a value lands on one of a stepped channel's own end positions."""

from ..fixture_capabilities import FixtureCapabilities


def is_a_step(capability: FixtureCapabilities, offset: int, value: int | None) -> bool:
    """Whether this value lands on one of the channel's own end positions.

    None - an EFX driving the channel to a value nobody can predict - is never
    a step: a swept blade is a crescent for most of its travel.
    """
    if value is None:
        return False
    ranges = capability.capabilities_by_offset[offset]
    ends = (min(r.minimum for r in ranges), max(r.maximum for r in ranges))
    return value in ends
