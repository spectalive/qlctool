"""Combine two simultaneous instants using QLC+'s HTP channel value."""

from .instant import Instant


def merge_instants(first: Instant, second: Instant) -> Instant:
    if not first.written:
        value, written = second.value, second.written
    elif not second.written:
        value, written = first.value, first.written
    elif first.value is None or second.value is None:
        value, written = None, True
    else:
        value, written = max(first.value, second.value), True
    return Instant(first.coloured or second.coloured, written, value)
