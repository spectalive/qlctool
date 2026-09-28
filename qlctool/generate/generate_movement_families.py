"""Movement per optics family: washes and beams stop sharing one geometry.

All twelve movers ran the same 100x100 EFX at the same speed, which tuned the
show for neither of them - a wash's soft wide beam wants big slow curves, a 7R
needle at that size and speed drags a hard line through faces (Codex review,
2026-08-27). The family split is read off capability: a mover with a gobo
wheel is a beam, one without is a wash - the same line `rule_movement_families`
draws.

Each family gets its own envelope per tempo of the night:

- **Suave** (Ambiente): two wide slow shapes per family. The beams used to hold
  the static fan through this whole level instead - four minutes of a needle
  nailed to one spot, which the room reads as broken rather than as rest ("las
  7R no se mueven", owner, 2026-08-29, watching AUTO). The fan is still their
  rest, but as one step of the Normal rotation, where it lasts a step and not a
  level.
- **Normal** (Fiesta): both families move, each at its own size and speed, and
  the fan sits in the beams' rotation as a rest step - stillness between
  moving blocks instead of motion as wallpaper.
- **Rapido** (Peak): both families, twice the pace, sized to their optics.

Every envelope is centred on its family's own measured audience window
(`audience_window`) rather than on mid-travel, which is where QLC+ puts a
figure nobody aims - the floor for the beams, the back wall for the washes -
and sized so the whole figure fits inside that window.

`Movimientos Cabezas` and `Movimientos Rapidos` remain the console's names for
"everything moves": Collections over the family chasers, so the buttons, the
moments and the muscle memory survive the split.
"""

from collections.abc import Collection

from .. import roles
from ..capabilities_of import capabilities_of
from ..efx_shape_identifiers import EFX_SHAPE_IDENTIFIERS
from ..fixture_library import FixtureLibrary
from ..functions.build_chaser import build_chaser
from ..functions.build_collection import build_collection
from ..names.default_names import default_names
from ..names.names import Names
from ..next_function_id import next_function_id
from ..rigged_fixture_ids import rigged_fixture_ids
from ..stage_ordered import stage_ordered
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
from .fit_rotated_figure import fit_rotated_figure
from .generate_cross_position import generate_cross_position
from .generate_fan_position import generate_fan_position
from .generate_movement_efx import generate_movement_efx
from .generate_wash_hold import generate_wash_hold
from .generated_families import GeneratedFamilies
from .movement_crossfade_ms import MOVEMENT_CROSSFADE_MS
from .wash_envelopes import (
    WASH,
    WASH_ALTERNATE,
    WASH_CASCADE,
    WASH_FAST,
    WASH_SLOW,
    WASH_TILT_WAVE,
    WASH_UNISON,
)


def generate_movement_families(
    workspace: Workspace,
    library: FixtureLibrary,
    mirrored_ids: Collection[int] = (),
    names: Names | None = None,
) -> GeneratedFamilies:
    """Per-family movement, the fan, and the two rig-wide Collections, named by `names`."""
    vocabulary = default_names() if names is None else names
    display = vocabulary.display

    def label_of(shape: str) -> str:
        return display(EFX_SHAPE_IDENTIFIERS[shape]) if shape in EFX_SHAPE_IDENTIFIERS else shape

    movement_path = display("path_movement")
    soft_path = display("path_soft_movement")
    fast_path = display("path_fast_movement")
    washes: list[int] = []
    beams: list[int] = []
    for caps in capabilities_of(workspace.root, library):
        if not (caps.has_role(roles.PAN) and caps.has_role(roles.TILT)):
            continue
        family = beams if caps.has_role(roles.GOBO) else washes
        family.append(caps.fixture.fixture_id)
    if not washes and not beams:
        # A rig with nothing that moves (2026-09-26, round G): no movement at
        # all, which every caller reads as "absent" from the empty families.
        return GeneratedFamilies()
    # Every figure takes the heads as the room sees them - rigged left to
    # right, spares after - so a spare never takes a phase slot or an
    # every-other place (en-sala DMX audit, 2026-09-26).
    rigged = rigged_fixture_ids(workspace.root)
    washes = stage_ordered(workspace.root, washes)
    beams = stage_ordered(workspace.root, beams)
    # A wave's offsets are loop/(heads+1) apart, so a spare in the row takes a
    # slot of it: six hidden washes put the two MACs a ninth of a loop apart
    # instead of a third (Round 2 review of the en-sala audit, 2026-09-27).
    # The waves run over the rigged heads alone, or every head when none is.
    rigged_washes = [i for i in washes if i in rigged] or washes
    rigged_beams = [i for i in beams if i in rigged] or beams

    def _family(
        ids,
        envelope,
        name,
        prefix,
        path,
        make_chaser=True,
        overrides=None,
        spread_phase=True,
        mirrored=None,
    ):
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
            shape: f"Wash {label_of(shape)} {display('mode_together')}" for shape in WASH.algorithms
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
            shape: f"Beam {label_of(shape)} {display('mode_together')}"
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
            shape: f"Wash {label_of(shape)} {display('mode_alternating')}"
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
            shape: f"Beam {label_of(shape)} {display('mode_alternating')}"
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

    fan_id = generate_fan_position(workspace, library, beams, names=vocabulary)
    cross_id = generate_cross_position(workspace, library, beams, names=vocabulary)
    rests = [function_id for function_id in (fan_id, cross_id) if function_id is not None]
    hold_id = generate_wash_hold(workspace, library, washes, names=vocabulary) if rests else None
    companions = {rest: [hold_id] for rest in rests} if hold_id is not None else {}

    # The Suave family gets its own cascade wave beside the two plain shapes.
    slow_wash_id: int | None = None
    if slow is not None:
        steps = list(slow.efx_ids) + (list(ola_suave.efx_ids) if ola_suave is not None else [])
        slow_wash_id = next_function_id(workspace.root)
        workspace.add_function(
            build_chaser(
                slow_wash_id,
                display("soft_washes"),
                steps,
                hold=WASH_SLOW.hold,
                fade_in=MOVEMENT_CROSSFADE_MS,
                fade_out=MOVEMENT_CROSSFADE_MS,
                run_order="Random",
                path=soft_path,
            )
        )

    slow_id: int | None = None
    slow_members = [
        member
        for member in (slow_wash_id, slow_beam.chaser_id if slow_beam else None)
        if member is not None
    ]
    if slow_members:
        slow_id = next_function_id(workspace.root)
        workspace.add_function(
            build_collection(slow_id, display("soft_movements"), slow_members, path=soft_path)
        )

    # The washes' rotation, assembled by hand like the beams' so the wave and
    # the push sit among its steps rather than on buttons only.
    wash_id: int | None = None
    if wash is not None:
        steps = (
            list(wash.efx_ids)
            + (list(wash_sim.efx_ids) if wash_sim is not None else [])
            + (list(ola_wash.efx_ids) if ola_wash is not None else [])
            + (list(unison_wash.efx_ids) if unison_wash is not None else [])
        )
        wash_id = next_function_id(workspace.root)
        workspace.add_function(
            build_chaser(
                wash_id,
                display("wash_movements"),
                steps,
                hold=WASH.hold,
                fade_in=MOVEMENT_CROSSFADE_MS,
                fade_out=MOVEMENT_CROSSFADE_MS,
                run_order="Random",
                path=movement_path,
            )
        )

    # The beams' rotation carries the fan as a step of its own: a rest the
    # chaser lands on, not a separate button somebody has to remember. The
    # cross is the other rest - an X where the fan is a crown - and the wave
    # and the push rotate among the moving blocks (a scene or EFX as a chaser
    # step is an alternative, never a concurrent writer, which is what keeps
    # `colores pisados` off the pan/tilt channels).
    beam_id: int | None = None
    if beam is not None:
        steps = (
            list(beam.efx_ids)
            + (list(beam_sim.efx_ids) if beam_sim is not None else [])
            + (list(beam_shapes.efx_ids) if beam_shapes is not None else [])
            + (list(cascada_beams.efx_ids) if cascada_beams is not None else [])
            + (list(ola_beam.efx_ids) if ola_beam is not None else [])
            + (list(unison_beam.efx_ids) if unison_beam is not None else [])
            + ([fan_id] if fan_id is not None else [])
            + ([cross_id] if cross_id is not None else [])
        )
        beam_id = next_function_id(workspace.root)
        workspace.add_function(
            build_chaser(
                beam_id,
                display("beam_movements"),
                steps,
                hold=BEAM.hold,
                fade_in=MOVEMENT_CROSSFADE_MS,
                fade_out=MOVEMENT_CROSSFADE_MS,
                run_order="Random",
                path=movement_path,
            )
        )

    # One entry per shape for the console, whichever families draw it. Diamond
    # and Leaf merge the beam versions into the same button the wash versions
    # already have; Ola Suave and Cascada Beams get a button of their own -
    # their algorithm (Line, Circle) already names an existing button, and
    # merging into it would fire a wash's plain Line whenever the cascade is
    # pressed, or vice versa.
    efx_ids: list[int] = []
    play_pick_ids: list[int] = []
    by_shape: dict[str, list[int]] = {}
    for generated, envelope in (
        (wash, WASH),
        (beam, BEAM),
        (beam_shapes, BEAM_ROTATED_SHAPES),
        (beam_wide, BEAM_WIDE_SHAPES),
    ):
        if generated is None:
            continue
        for shape, efx in zip(envelope.algorithms, generated.efx_ids, strict=True):
            by_shape.setdefault(shape, []).append(efx)
    for shape in WASH.algorithms:
        members = by_shape.get(shape)
        if not members:
            continue
        collection_id = next_function_id(workspace.root)
        workspace.add_function(
            build_collection(
                collection_id,
                vocabulary.render("movement_shape", shape=label_of(shape)),
                members,
                path=movement_path,
            )
        )
        efx_ids.append(collection_id)
        play_pick_ids.append(collection_id)
    # The twins the hand-built console had and this one only ran inside the
    # automatic rotation: "faltan movimientos, unos iban a la vez otros iban
    # alternados" (owner, 2026-09-22). One button per shape and per way of
    # phasing it, each spanning both families like the plain shapes do.
    for mode, parts in (
        ("mode_together", ((wash_sim, WASH), (beam_sim, BEAM_TWIN_SHAPES))),
        ("mode_alternating", ((wash_alt, WASH_ALTERNATE), (beam_alt, BEAM_ALTERNATE))),
    ):
        twins: dict[str, list[int]] = {}
        for generated, envelope in parts:
            if generated is None:
                continue
            for shape, efx in zip(envelope.algorithms, generated.efx_ids, strict=True):
                twins.setdefault(shape, []).append(efx)
        for shape in WASH.algorithms:
            members = twins.get(shape)
            if not members:
                continue
            collection_id = next_function_id(workspace.root)
            workspace.add_function(
                build_collection(
                    collection_id,
                    vocabulary.render("movement_shape", shape=f"{label_of(shape)} {display(mode)}"),
                    members,
                    path=movement_path,
                )
            )
            efx_ids.append(collection_id)
            play_pick_ids.append(collection_id)
    if ola_suave is not None:
        efx_ids.append(ola_suave.efx_ids[0])
    if cascada_beams is not None:
        efx_ids.append(cascada_beams.efx_ids[0])

    # The wave and the push span both families, so their buttons are
    # Collections the way Diamond and Leaf are - one press, both optics.
    def _figure(name, *parts):
        members = [generated.efx_ids[0] for generated in parts if generated is not None]
        if not members:
            return
        collection_id = next_function_id(workspace.root)
        workspace.add_function(
            build_collection(
                collection_id,
                name,
                members,
                path=movement_path,
            )
        )
        efx_ids.append(collection_id)
        play_pick_ids.append(collection_id)

    _figure(display("vertical_wave"), ola_wash, ola_beam)
    # On the beams alone the push is `Linea Simultaneo` under another name -
    # same line, size, speed and phase - which is a second button for one
    # look (`twin_movement`, 2026-09-26): only the washes' slow push makes it
    # a figure of its own.
    if unison_wash is not None:
        _figure(display("unison_sweep"), unison_wash, unison_beam)
    play_pick_ids += [function_id for function_id in (fan_id, cross_id) if function_id is not None]

    def _both(name, first, second, path):
        members = [m for m in (first, second) if m is not None]
        if not members:
            return None
        collection_id = next_function_id(workspace.root)
        workspace.add_function(build_collection(collection_id, name, members, path=path))
        return collection_id

    fast_wash_id = fast_wash.chaser_id if fast_wash is not None else None
    fast_beam_id = fast_beam.chaser_id if fast_beam is not None else None
    return GeneratedFamilies(
        slow_id=slow_id,
        slow_beam_id=slow_beam.chaser_id if slow_beam is not None else None,
        wash_id=wash_id,
        beam_id=beam_id,
        fast_wash_id=fast_wash_id,
        fast_beam_id=fast_beam_id,
        fan_id=fan_id,
        cabezas_id=_both(display("head_movements"), wash_id, beam_id, movement_path),
        rapidos_id=_both(
            display("fast_movements"),
            fast_wash_id,
            fast_beam_id,
            fast_path,
        ),
        efx_ids=efx_ids,
        play_pick_ids=play_pick_ids,
        dial_ids=[m for m in (wash_id, beam_id) if m is not None],
        pick_companions=companions,
    )
