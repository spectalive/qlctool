"""Every per-family movement variant generate_movement_families builds, bundled for assembly.

generate_family_variants fills one of these; the rotation, shape-button and
figure-button stages each read the fields they need off it. None means that
variant's fixture list was empty (no washes, no beams, or too few rigged heads
for a twin).
"""

from dataclasses import dataclass

from .generated_movements import GeneratedMovements


@dataclass(frozen=True)
class FamilyVariants:
    slow: GeneratedMovements | None
    slow_beam: GeneratedMovements | None
    ola_suave: GeneratedMovements | None
    wash: GeneratedMovements | None
    beam: GeneratedMovements | None
    wash_sim: GeneratedMovements | None
    beam_sim: GeneratedMovements | None
    beam_shapes: GeneratedMovements | None
    beam_wide: GeneratedMovements | None
    wash_alt: GeneratedMovements | None
    beam_alt: GeneratedMovements | None
    cascada_beams: GeneratedMovements | None
    ola_wash: GeneratedMovements | None
    ola_beam: GeneratedMovements | None
    unison_wash: GeneratedMovements | None
    unison_beam: GeneratedMovements | None
    fast_wash: GeneratedMovements | None
    fast_beam: GeneratedMovements | None
