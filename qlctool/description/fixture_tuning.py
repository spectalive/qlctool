"""Values a show sets on fixture channels that no capability decides for it."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FixtureTuning:
    """Beam focus, prism spin, flash strobe speeds and the talk light's white."""

    beam_focus: int
    prism_spin_slow: int
    strobe_fast: float
    strobe_slow: float
    talk_white: tuple[int, int, int]
