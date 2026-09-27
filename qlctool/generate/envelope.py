"""One family's movement at one tempo: shapes, size, and speed.

propagation and rotation apply to every algorithm in the envelope;
rotation_by_algorithm overrides rotation per shape, for an envelope that
mixes shapes wanting different angles (e.g. Diamond and Leaf).

width and height are the reach the envelope allows on pan and tilt. An
unturned shape reaches exactly its size; a turned one reaches further, so
fit_rotated redraws every turned shape at the largest size whose reach
stays inside them (`fit_rotated_figure`). Without it Diamante, turned 90
degrees at Width 20 Height 13, swung the 7R to tilt 200-240 over a 207-234
window (en-sala DMX re-audit, 2026-09-27).
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Envelope:
    algorithms: tuple[str, ...]
    duration: int
    width: int
    height: int
    hold: int
    propagation: str = "Parallel"
    rotation: int = 0
    rotation_by_algorithm: dict[str, int] = field(default_factory=dict)
    fit_rotated: bool = False
    # Where the figure is centred in raw pan and tilt. 127 is mid-travel, which
    # is what QLC+ writes when nobody says - not a place (`movement_aim`).
    pan_offset: int = 127
    tilt_offset: int = 127
