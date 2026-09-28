"""The alternating, wave, push and fast movement variants generate_wave_variants builds.

generate_family_variants combines this bundle with PlainVariants into the
final FamilyVariants the rotation and button stages read.
"""

from dataclasses import dataclass

from .generated_movements import GeneratedMovements


@dataclass(frozen=True)
class WaveVariants:
    wash_alt: GeneratedMovements | None
    beam_alt: GeneratedMovements | None
    cascada_beams: GeneratedMovements | None
    ola_wash: GeneratedMovements | None
    ola_beam: GeneratedMovements | None
    unison_wash: GeneratedMovements | None
    unison_beam: GeneratedMovements | None
    fast_wash: GeneratedMovements | None
    fast_beam: GeneratedMovements | None
