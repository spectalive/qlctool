"""One room state: everything that runs while it is the state."""

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Moment:
    name: str
    members: Sequence[int | None]
