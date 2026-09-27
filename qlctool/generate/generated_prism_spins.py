"""What generate_prism_spins built: the extra spin scenes."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedPrismSpins:
    scene_ids: list[int]
