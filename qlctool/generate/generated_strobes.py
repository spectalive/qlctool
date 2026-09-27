"""What generate_strobe_effects built: the latched pair and the two held scenes."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedStrobes:
    on_id: int | None
    off_id: int | None
    fast_id: int
    medium_id: int
