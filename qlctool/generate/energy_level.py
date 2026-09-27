"""One level: what runs on top of the colour bed, and for how long."""

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class EnergyLevel:
    name: str
    members: Sequence[int]
    hold: int
