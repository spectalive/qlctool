"""Generate every per-family movement variant: plain, twin, alternate, wave, push, fast.

The first stage of generate_movement_families - the plain shapes and twins
(generate_plain_variants), then the alternates, waves, pushes and fast passes
(generate_wave_variants), combined into the FamilyVariants the rotation and
button stages then assemble. Creation order here is the order the fixed
EFX/chaser ids come out in, so it must not change independently of the
console pages it feeds.
"""

from collections.abc import Collection, Sequence

from ..fixture_library import FixtureLibrary
from ..names.names import Names
from ..workspace import Workspace
from .family_variants import FamilyVariants
from .generate_plain_variants import generate_plain_variants
from .generate_wave_variants import generate_wave_variants


def generate_family_variants(
    workspace: Workspace,
    library: FixtureLibrary,
    washes: Sequence[int],
    beams: Sequence[int],
    rigged: set[int],
    rigged_washes: Sequence[int],
    rigged_beams: Sequence[int],
    mirrored_ids: Collection[int],
    vocabulary: Names,
    movement_path: str,
    soft_path: str,
    fast_path: str,
) -> FamilyVariants:
    plain = generate_plain_variants(
        workspace,
        library,
        washes,
        beams,
        rigged,
        rigged_washes,
        rigged_beams,
        mirrored_ids,
        vocabulary,
        movement_path,
        soft_path,
    )
    wave = generate_wave_variants(
        workspace,
        library,
        washes,
        beams,
        rigged,
        rigged_washes,
        rigged_beams,
        mirrored_ids,
        vocabulary,
        movement_path,
        fast_path,
    )
    return FamilyVariants(
        slow=plain.slow,
        slow_beam=plain.slow_beam,
        ola_suave=plain.ola_suave,
        wash=plain.wash,
        beam=plain.beam,
        wash_sim=plain.wash_sim,
        beam_sim=plain.beam_sim,
        beam_shapes=plain.beam_shapes,
        beam_wide=plain.beam_wide,
        wash_alt=wave.wash_alt,
        beam_alt=wave.beam_alt,
        cascada_beams=wave.cascada_beams,
        ola_wash=wave.ola_wash,
        ola_beam=wave.ola_beam,
        unison_wash=wave.unison_wash,
        unison_beam=wave.unison_beam,
        fast_wash=wave.fast_wash,
        fast_beam=wave.fast_beam,
    )
