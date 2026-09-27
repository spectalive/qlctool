"""What generate_movement_efx built: one function per shape, plus its parts."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GeneratedMovements:
    # What the console and the chaser see: one function per shape. When the
    # movers had to be split it is a Collection running both halves at once.
    efx_ids: list[int]
    chaser_id: int | None
    # The EFX underneath, when a split happened. Empty when there was none.
    part_ids: list[int] = field(default_factory=list)
