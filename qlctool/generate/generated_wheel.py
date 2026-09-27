"""What generate_wheel_scenes built: the wheel's positions and its chaser."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedWheel:
    scene_ids: list[int]
    chaser_id: int | None
