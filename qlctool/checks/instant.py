"""One possible output for a channel and the colour running beside it."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Instant:
    coloured: bool
    written: bool
    value: int | None
