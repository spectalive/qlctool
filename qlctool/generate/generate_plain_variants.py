"""Generate the plain-shape families and their twins: slow, normal and the "juntos" pair.

The first nine of generate_family_variants' eighteen family_variant calls, in
the order the console's original ids came out.
"""

from collections.abc import Collection, Sequence
from functools import partial

from ..fixture_library import FixtureLibrary
from ..names.names import Names
from ..workspace import Workspace
from .beam_envelopes import BEAM, BEAM_ROTATED_SHAPES, BEAM_SLOW, BEAM_TWIN_SHAPES, BEAM_WIDE_SHAPES
from .envelope import Envelope
from .family_variant import family_variant
from .generated_movements import GeneratedMovements
from .label_of import label_of
from .plain_variants import PlainVariants
from .wash_envelopes import WASH, WASH_CASCADE, WASH_SLOW


def generate_plain_variants(
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
) -> PlainVariants:
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

    slow = _variant(washes, WASH_SLOW, None, display("prefix_soft"), soft_path, make_chaser=False)
    slow_beam = _variant(
        beams, BEAM_SLOW, display("soft_beams"), display("prefix_soft_beam"), soft_path
    )
    ola_suave = _variant(
        rigged_washes,
        WASH_CASCADE,
        None,
        display("prefix_wave"),
        soft_path,
        make_chaser=False,
        overrides={"Line": display("soft_wave")},
        spread_phase=False,
    )
    wash = _variant(washes, WASH, None, "Wash", movement_path, make_chaser=False)
    beam = _variant(beams, BEAM, None, "Beam", movement_path, make_chaser=False)
    # The old "(Simultaneo)" twins: same shapes, same envelope, every head at
    # phase 0 so the family traces one figure together. One rigged head traces
    # the same figure alone either way, so it gets no twin (`twin_movement`;
    # the lone fixture, 2026-09-27).
    wash_sim = _variant(
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
    beam_sim = _variant(
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
    beam_shapes = _variant(
        beams, BEAM_ROTATED_SHAPES, None, "Beam", movement_path, make_chaser=False
    )
    beam_wide = _variant(beams, BEAM_WIDE_SHAPES, None, "Beam", movement_path, make_chaser=False)

    return PlainVariants(
        slow=slow,
        slow_beam=slow_beam,
        ola_suave=ola_suave,
        wash=wash,
        beam=beam,
        wash_sim=wash_sim,
        beam_sim=beam_sim,
        beam_shapes=beam_shapes,
        beam_wide=beam_wide,
    )
