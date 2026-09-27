"""What generate_rainbow_efx built: the two whole-rig rainbow EFX, if any."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedRainbows:
    simultaneo_id: int | None = None
    pasos_id: int | None = None
