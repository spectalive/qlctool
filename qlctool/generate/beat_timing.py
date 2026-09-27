"""A function's step timing in beats: how long it fades, how long it holds."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BeatTiming:
    hold: float
    fade: float = 0.0
