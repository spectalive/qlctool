"""Generate every per-family movement variant: plain, twin, alternate, wave, push, fast.

The first stage of generate_movement_families - one generate_movement_efx call
per shape set, bundled into a FamilyVariants the rotation and button stages
then assemble. Creation order here is the order the fixed EFX/chaser ids come
out in, so it must not change independently of the console pages it feeds.
"""

from collections.abc import Collection, Sequence
from functools import partial

from ..fixture_library import FixtureLibrary
from ..names.names import Names
from ..workspace import Workspace
from .alternate_mirror import alternate_mirror
from .beam_envelopes import (
    BEAM,
    BEAM_ALTERNATE,
    BEAM_CASCADE,
    BEAM_FAST,
    BEAM_ROTATED_SHAPES,
    BEAM_SLOW,
    BEAM_TILT_WAVE,
    BEAM_TWIN_SHAPES,
    BEAM_UNISON,
    BEAM_WIDE_SHAPES,
)
from .envelope import Envelope
from .family_variants import FamilyVariants
from .fit_rotated_figure import fit_rotated_figure
from .generate_movement_efx import generate_movement_efx
from .generated_movements import GeneratedMovements
from .label_of import label_of
from .wash_envelopes import (
    WASH,
    WASH_ALTERNATE,
    WASH_CASCADE,
    WASH_FAST,
    WASH_SLOW,
    WASH_TILT_WAVE,
    WASH_UNISON,
)


def generate_family_variants(
    workspace: Workspace,
    library: FixtureLibrary,
    washes: Sequence[int],
    beams: Sequence[int],
    rigged: Collection[int],
    rigged_washes: Sequence[int],
    rigged_beams: Sequence[int],
    mirrored_ids: Collection[int],
    vocabulary: Names,
    movement_path: str,
    soft_path: str,
    fast_path: str,
) -> FamilyVariants:
    display = vocabulary.display
    label = partial(label_of, display)

    def _family(
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

    slow = _family(washes, WASH_SLOW, None, display("prefix_soft"), soft_path, make_chaser=False)
    slow_beam = _family(
        beams, BEAM_SLOW, display("soft_beams"), display("prefix_soft_beam"), soft_path
    )
    ola_suave = _family(
        rigged_washes,
        WASH_CASCADE,
        None,
        display("prefix_wave"),
        soft_path,
        make_chaser=False,
        overrides={"Line": display("soft_wave")},
        spread_phase=False,
    )
    wash = _family(washes, WASH, None, "Wash", movement_path, make_chaser=False)
    beam = _family(beams, BEAM, None, "Beam", movement_path, make_chaser=False)
    # The old "(Simultaneo)" twins: same shapes, same envelope, every head at
    # phase 0 so the family traces one figure together. One rigged head traces
    # the same figure alone either way, so it gets no twin (`twin_movement`;
    # the lone fixture, 2026-09-27).
    wash_sim = _family(
        washes if len(rigged_washes) > 1 else [],
        WASH,
        None,
        "Wash",
        movement_path,
        make_chaser=False,
        overrides={
            shape: f"Wash {label(shape)} {display('mode_together')}" for shape in WASH.algorithms
        },
        spread_phase=False,
    )
    beam_sim = _family(
        beams if len(rigged_beams) > 1 else [],
        BEAM_TWIN_SHAPES,
        None,
        "Beam",
        movement_path,
        make_chaser=False,
        overrides={
            shape: f"Beam {label(shape)} {display('mode_together')}"
            for shape in BEAM_TWIN_SHAPES.algorithms
        },
        spread_phase=False,
    )
    beam_shapes = _family(
        beams, BEAM_ROTATED_SHAPES, None, "Beam", movement_path, make_chaser=False
    )
    beam_wide = _family(beams, BEAM_WIDE_SHAPES, None, "Beam", movement_path, make_chaser=False)
    # Each head against its neighbour: the same figure with every other rigged
    # head across the stage running it backwards, which is the "cada cabeza
    # para un lado" the owner missed (`alternate_mirror`, ruling D5).
    wash_alt = _family(
        washes,
        WASH_ALTERNATE,
        None,
        "Wash",
        movement_path,
        make_chaser=False,
        overrides={
            shape: f"Wash {label(shape)} {display('mode_alternating')}"
            for shape in WASH_ALTERNATE.algorithms
        },
        mirrored=alternate_mirror([i for i in washes if i in rigged], mirrored_ids),
    )
    beam_alt = _family(
        beams,
        BEAM_ALTERNATE,
        None,
        "Beam",
        movement_path,
        make_chaser=False,
        overrides={
            shape: f"Beam {label(shape)} {display('mode_alternating')}"
            for shape in BEAM_ALTERNATE.algorithms
        },
        mirrored=alternate_mirror([i for i in beams if i in rigged], mirrored_ids),
    )
    cascada_beams = _family(
        rigged_beams,
        BEAM_CASCADE,
        None,
        # No prefix: the envelope's one shape, Circle, is named by the override.
        None,
        movement_path,
        make_chaser=False,
        overrides={"Circle": display("cascade_beams")},
        spread_phase=False,
    )
    # The tilt wave and the synced push, per family like every figure. A
    # cascade's phase is its propagation: a spread on top of it, or a reversed
    # side on a tilt that has no left and right, turned the two MACs' wave into
    # a see-saw (Round 2 review of the en-sala audit, 2026-09-27).
    ola_wash = _family(
        rigged_washes,
        WASH_TILT_WAVE,
        None,
        display("prefix_wave"),
        movement_path,
        make_chaser=False,
        overrides={"Line": display("vertical_wave_washes")},
        spread_phase=False,
        mirrored=(),
    )
    ola_beam = _family(
        rigged_beams,
        BEAM_TILT_WAVE,
        None,
        display("prefix_wave"),
        movement_path,
        make_chaser=False,
        overrides={"Line": display("vertical_wave_beams")},
        spread_phase=False,
        mirrored=(),
    )
    unison_wash = _family(
        washes,
        WASH_UNISON,
        None,
        display("prefix_sweep"),
        movement_path,
        make_chaser=False,
        overrides={"Line": display("unison_sweep_washes")},
        spread_phase=False,
    )
    unison_beam = _family(
        beams,
        BEAM_UNISON,
        None,
        display("prefix_sweep"),
        movement_path,
        make_chaser=False,
        overrides={"Line": display("unison_sweep_beams")},
        spread_phase=False,
    )
    fast_wash = _family(
        washes, WASH_FAST, display("fast_washes"), display("prefix_fast_wash"), fast_path
    )
    fast_beam = _family(
        beams, BEAM_FAST, display("fast_beams"), display("prefix_fast_beam"), fast_path
    )

    return FamilyVariants(
        slow=slow,
        slow_beam=slow_beam,
        ola_suave=ola_suave,
        wash=wash,
        beam=beam,
        wash_sim=wash_sim,
        beam_sim=beam_sim,
        beam_shapes=beam_shapes,
        beam_wide=beam_wide,
        wash_alt=wash_alt,
        beam_alt=beam_alt,
        cascada_beams=cascada_beams,
        ola_wash=ola_wash,
        ola_beam=ola_beam,
        unison_wash=unison_wash,
        unison_beam=unison_beam,
        fast_wash=fast_wash,
        fast_beam=fast_beam,
    )
