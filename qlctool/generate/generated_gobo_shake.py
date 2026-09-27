"""What generate_gobo_shake built: the shake bursts' scenes."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GeneratedGoboShake:
    scene_ids: list[int] = field(default_factory=list)
