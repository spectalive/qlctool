"""The rig's washes and beams, stage-ordered, plus the paths their picks live under.

resolve_movement_rig fills one of these; every later stage of
generate_movement_families reads the fields it needs off it instead of
recomputing them.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MovementRig:
    washes: list[int]
    beams: list[int]
    rigged: set[int]
    rigged_washes: list[int]
    rigged_beams: list[int]
    movement_path: str
    soft_path: str
    fast_path: str
