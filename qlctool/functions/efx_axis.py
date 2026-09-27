"""One axis of an EFX path: its centre, how fast it cycles, its phase."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EFXAxis:
    """One axis of the path: its centre, how fast it cycles, its phase."""

    offset: int = 127
    frequency: int = 2
    phase: int = 0
