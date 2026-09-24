"""A step timing in beats: `{ hold = 8, fade = 1 }`."""

from typing import Any

from ...generate.beat_tempo import BeatTiming
from .reject_unknown_keys import reject_unknown_keys


def beat_timing_value(value: Any, where: str) -> BeatTiming:
    """The BeatTiming, with a positive hold and a fade of zero or more."""
    if not isinstance(value, dict):
        raise ValueError(f"{where}: a beat timing is {{ hold = <beats>, fade = <beats> }}")
    reject_unknown_keys(value, ("hold", "fade"), where)
    hold, fade = value.get("hold"), value.get("fade", 0)
    numbers = all(isinstance(n, (int, float)) and not isinstance(n, bool) for n in (hold, fade))
    if not numbers or hold <= 0 or fade < 0:
        raise ValueError(f"{where}: hold is a positive number of beats and fade zero or more")
    return BeatTiming(hold=hold, fade=fade)
