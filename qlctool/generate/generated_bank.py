"""One fixture group's colour bank: its scenes, splits, wheels and console keys."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GeneratedBank:
    group_name: str
    scene_ids: list[int] = field(default_factory=list)
    split_ids: list[int] = field(default_factory=list)
    wheel_id: int | None = None
    mix_wheel_id: int | None = None
    # What the console binds to keys 1-0: eight solids, then the old blue/red
    # and red/blue splits on 9 and 0. Falls back to plain solids when a group
    # cannot show a split.
    key_ids: list[int] = field(default_factory=list)
