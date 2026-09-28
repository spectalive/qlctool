"""Generate the alternating, wave, push and fast families: the last nine variants.

The last nine of generate_family_variants' eighteen family_variant calls, in
the order the console's original ids came out.
"""

from collections.abc import Collection, Sequence
from functools import partial

from ..fixture_library import FixtureLibrary
from ..names.names import Names
from ..workspace import Workspace
from .alternate_mirror import alternate_mirror
from .beam_envelopes import BEAM_ALTERNATE, BEAM_CASCADE, BEAM_FAST, BEAM_TILT_WAVE, BEAM_UNISON
from .envelope import Envelope
from .family_variant import family_variant
from .generated_movements import GeneratedMovements
from .label_of import label_of
from .wash_envelopes import WASH_ALTERNATE, WASH_FAST, WASH_TILT_WAVE, WASH_UNISON
from .wave_variants import WaveVariants


def generate_wave_variants(
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
    fast_path: str,
) -> WaveVariants:
    display = vocabulary.display
    label = partial(label_of, display)

    def _variant(
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
        return family_variant(
            workspace,
            library,
            vocabulary,
            rigged,
            mirrored_ids,
            ids,
            envelope,
            name,
            prefix,
            path,
            make_chaser=make_chaser,
            overrides=overrides,
            spread_phase=spread_phase,
            mirrored=mirrored,
        )

    # Each head against its neighbour: the same figure with every other rigged
    # head across the stage running it backwards, which is the "cada cabeza
    # para un lado" the owner missed (`alternate_mirror`, ruling D5).
    wash_alt = _variant(
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
    beam_alt = _variant(
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
    cascada_beams = _variant(
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
    ola_wash = _variant(
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
    ola_beam = _variant(
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
    unison_wash = _variant(
        washes,
        WASH_UNISON,
        None,
        display("prefix_sweep"),
        movement_path,
        make_chaser=False,
        overrides={"Line": display("unison_sweep_washes")},
        spread_phase=False,
    )
    unison_beam = _variant(
        beams,
        BEAM_UNISON,
        None,
        display("prefix_sweep"),
        movement_path,
        make_chaser=False,
        overrides={"Line": display("unison_sweep_beams")},
        spread_phase=False,
    )
    fast_wash = _variant(
        washes, WASH_FAST, display("fast_washes"), display("prefix_fast_wash"), fast_path
    )
    fast_beam = _variant(
        beams, BEAM_FAST, display("fast_beams"), display("prefix_fast_beam"), fast_path
    )

    return WaveVariants(
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
