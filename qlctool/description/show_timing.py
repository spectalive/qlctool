"""How long the night spends where, and the beat its chases count in."""

from collections.abc import Mapping
from dataclasses import dataclass

from ..generate.beat_tempo import BeatTiming


@dataclass(frozen=True)
class ShowTiming:
    """Every duration the generated show is written against: milliseconds, or beats."""

    bpm: int
    ambient_ms: int
    party_ms: int
    peak_ms: int
    dynamic_ms: int
    dynamic_chase_ms: int
    dynamic_pingpong_ms: int
    panel_effects_ms: int
    panel_manual_ms: int
    prism_step_ms: int
    beat_timings: Mapping[str, BeatTiming]
    matrix_beats: BeatTiming
    beats: bool = False

    @property
    def beat_ms(self) -> int:
        """One beat at `bpm`: what the tap dials start on and count multipliers in."""
        return 60_000 // self.bpm
