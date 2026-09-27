"""What generate_channel_probe built: the fixture it probed and its scenes."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedProbe:
    fixture_id: int
    scene_ids: list[int]
    chaser_id: int | None
