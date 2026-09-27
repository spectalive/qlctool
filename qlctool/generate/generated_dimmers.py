"""What generate_dimmer_chases built: the two chases, the ping-pong and its parts."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GeneratedDimmers:
    # One function per look, whatever it took to build it: when the dimmable
    # fixtures had to be split, each chase ID is a Collection over its own
    # halves, and part_ids carries the parts for both directions.
    chase_id: int
    chase2_id: int
    # None when only one fixture dims: a ping-pong of one fixture has no odd
    # half, so it is a looping strobe on a button (2026-09-27).
    pingpong_id: int | None
    scene_ids: list[int]
    part_ids: list[int] = field(default_factory=list)
