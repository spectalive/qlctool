"""`count` positions spread evenly across a wheel's patterns."""

from collections.abc import Sequence

from ..definition import Capability


def spaced(patterns: Sequence[Capability], count: int) -> list[Capability]:
    if len(patterns) <= count:
        return list(patterns)
    return [patterns[round(i * (len(patterns) - 1) / (count - 1))] for i in range(count)]
