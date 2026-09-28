"""The plain-shape and twin movement variants generate_plain_variants builds.

generate_wave_variants and the rotation/button stages read these back off
FamilyVariants once generate_family_variants has combined this bundle with
WaveVariants.
"""

from dataclasses import dataclass

from .generated_movements import GeneratedMovements


@dataclass(frozen=True)
class PlainVariants:
    slow: GeneratedMovements | None
    slow_beam: GeneratedMovements | None
    ola_suave: GeneratedMovements | None
    wash: GeneratedMovements | None
    beam: GeneratedMovements | None
    wash_sim: GeneratedMovements | None
    beam_sim: GeneratedMovements | None
    beam_shapes: GeneratedMovements | None
    beam_wide: GeneratedMovements | None
