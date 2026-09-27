"""What generate_builtin_effects built: its scenes, chaser and touched fixtures."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GeneratedBuiltins:
    scene_ids: list[int] = field(default_factory=list)
    chaser_id: int | None = None
    fixture_ids: tuple[int, ...] = ()
    # (fixture id, channel offset) of every speed channel the scenes set, so
    # the console can put a live fader over them the way the hand-built show
    # did ("Strobo LED Effect Speed").
    speed_channels: tuple[tuple[int, int], ...] = ()
