"""Generate one family's movement variant: an EFX per shape, sized for its envelope.

The one call generate_movement_families makes eighteen times, once per family
variant - the plain shapes, the twins, the alternates, the waves, the pushes,
the fast passes. Pulled out of its old closure so each stage that builds a
group of variants can call it without capturing the whole rig.
"""

from collections.abc import Collection, Sequence

from ..fixture_library import FixtureLibrary
from ..names.names import Names
from ..workspace import Workspace
from .envelope import Envelope
from .fit_rotated_figure import fit_rotated_figure
from .generate_movement_efx import generate_movement_efx
from .generated_movements import GeneratedMovements


def family_variant(
    workspace: Workspace,
    library: FixtureLibrary,
    vocabulary: Names,
    rigged: Collection[int],
    mirrored_ids: Collection[int],
    ids: Sequence[int],
    envelope: Envelope,
    name: str | None,
    prefix: str | None,
    path: str,
    make_chaser: bool = True,
    overrides: dict[str, str] | None = None,
    spread_phase: bool = True,
    mirrored: Collection[int] | None = None,
) -> GeneratedMovements | None:
    if not ids:
        return None
    sizes = {
        algorithm: fit_rotated_figure(
            algorithm,
            envelope.rotation_by_algorithm.get(algorithm, envelope.rotation),
            envelope.width,
            envelope.height,
        )
        for algorithm in envelope.algorithms
        if envelope.fit_rotated
        and envelope.rotation_by_algorithm.get(algorithm, envelope.rotation) % 360
    }
    return generate_movement_efx(
        workspace,
        library,
        algorithms=envelope.algorithms,
        fixture_ids=ids,
        path=path,
        make_chaser=make_chaser,
        duration=envelope.duration,
        width=envelope.width,
        height=envelope.height,
        chaser_hold=envelope.hold,
        chaser_run_order="Random",
        chaser_name=name,
        label_prefix=prefix,
        mirrored_ids=mirrored_ids if mirrored is None else mirrored,
        propagation_mode=envelope.propagation,
        rotation=envelope.rotation,
        rotation_by_algorithm=envelope.rotation_by_algorithm or None,
        size_by_algorithm=sizes or None,
        names=overrides,
        spread_phase=spread_phase,
        pan_offset=envelope.pan_offset,
        tilt_offset=envelope.tilt_offset,
        vocabulary=vocabulary,
        rigged_ids=rigged,
    )
