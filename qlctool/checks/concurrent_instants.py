"""Combine every simultaneous pair using QLC+'s HTP channel value."""

from .instant import Instant
from .merge_instants import merge_instants


def concurrent_instants(
    first: frozenset[Instant], second: frozenset[Instant]
) -> frozenset[Instant]:
    return frozenset(merge_instants(left, right) for left in first for right in second)
