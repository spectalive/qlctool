"""What generate_energy_levels built: each level's Collection and the cycle Chaser."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GeneratedEnergy:
    level_ids: dict[str, int] = field(default_factory=dict)
    cycle_id: int | None = None
