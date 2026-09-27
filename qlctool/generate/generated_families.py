"""What generate_movement_families built: each family's functions and picks."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GeneratedFamilies:
    slow_id: int | None = None
    slow_beam_id: int | None = None
    wash_id: int | None = None
    beam_id: int | None = None
    fast_wash_id: int | None = None
    fast_beam_id: int | None = None
    fan_id: int | None = None
    # The console's names for "everything moves", spanning both families.
    cabezas_id: int | None = None
    rapidos_id: int | None = None
    # One entry per shape for the console's solo frame, and the chasers the
    # speed dial drives.
    efx_ids: list[int] = field(default_factory=list)
    # Exact movement functions the play page may wrap as manual picks.
    play_pick_ids: list[int] = field(default_factory=list)
    dial_ids: list[int] = field(default_factory=list)
    # What a play pick starts beside its function: the washes held at their
    # window while a beam-only look is picked (`generate_wash_hold`).
    pick_companions: dict[int, list[int]] = field(default_factory=dict)
