"""What generate_energy_intensity built: the ambient and full intensity scenes."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedIntensity:
    ambient_id: int | None
    full_id: int | None
