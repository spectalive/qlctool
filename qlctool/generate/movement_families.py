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
from dataclasses import dataclass, field

from .. import roles
from ..capabilities_of import capabilities_of
from ..efx_shape_identifiers import EFX_SHAPE_IDENTIFIERS
from ..every_other import every_other
from ..functions.chaser import build_chaser
from ..functions.collection import build_collection
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..names.default_names import default_names
from ..names.names import Names
from ..workspace import Workspace
from .cross_position import generate_cross_position
from .fan_position import generate_fan_position
from .movement_aim import (
    BEAM_PAN_AIM,
    BEAM_PAN_SPAN,
    BEAM_TILT_AIM,
    BEAM_TILT_SPAN,
    WASH_PAN_AIM,
    WASH_PAN_SPAN,
    WASH_TILT_AIM,
    WASH_TILT_SPAN,
)
from .movement_efx import generate_movement_efx


@dataclass(frozen=True)
class Envelope:
    """One family's movement at one tempo: shapes, size, and speed.

    propagation and rotation apply to every algorithm in the envelope;
    rotation_by_algorithm overrides rotation per shape, for an envelope that
    mixes shapes wanting different angles (e.g. Diamond and Leaf).
    """

    algorithms: tuple[str, ...]
    duration: int
    width: int
    height: int
    hold: int
    propagation: str = "Parallel"
    rotation: int = 0
    rotation_by_algorithm: dict[str, int] = field(default_factory=dict)
    # Where the figure is centred in raw pan and tilt. 127 is mid-travel, which
    # is what QLC+ writes when nobody says - not a place (`movement_aim`).
    pan_offset: int = 127
    tilt_offset: int = 127


# Sizes and durations are QLC+ raw EFX values, not degrees: a starting
# envelope for on-site tuning, not a universal standard.
# Both families are sized by their own measured window, not by taste: a figure
# bigger than the window is a head pointing out of the room, whatever the
# optics. Slow draws the same shape smaller, which is the room left to vary.
WASH_SLOW = Envelope(
    ("Circle", "Line"),
    28000,
    WASH_PAN_SPAN * 2 // 3,
    WASH_TILT_SPAN * 2 // 3,
    56000,
    pan_offset=WASH_PAN_AIM,
    tilt_offset=WASH_TILT_AIM,
)
# The beam sizes are the audience window, not a taste: the window is 41 counts
# of pan by 27 of tilt, so a figure any bigger walks out of the room. Slow is
# the same shape drawn smaller and slower, which is the only room left to vary.
BEAM_SLOW = Envelope(
    ("Circle", "Line"),
    # The slow family shares the washes' figure time for the same reason.
    28000,
    BEAM_PAN_SPAN * 2 // 3,
    BEAM_TILT_SPAN * 2 // 3,
    56000,
    pan_offset=BEAM_PAN_AIM,
    tilt_offset=BEAM_TILT_AIM,
)
WASH = Envelope(
    ("Circle", "Eight", "Line", "Diamond", "Square", "Leaf", "Lissajous"),
    16000,
    WASH_PAN_SPAN,
    WASH_TILT_SPAN,
    10000,
    pan_offset=WASH_PAN_AIM,
    tilt_offset=WASH_TILT_AIM,
)
BEAM = Envelope(
    ("Circle", "Eight", "Line"),
    # Half the washes' figure, so the two families rhyme instead of drifting:
    # one wash curve to two beam curves, the same 10 s hold under both ("hay
    # que mirar la sincronizacion para que tengan sentido", owner, 2026-09-22).
    WASH.duration // 2,
    BEAM_PAN_SPAN,
    BEAM_TILT_SPAN,
    10000,
    pan_offset=BEAM_PAN_AIM,
    tilt_offset=BEAM_TILT_AIM,
)
WASH_FAST = Envelope(
    WASH.algorithms,
    5000,
    WASH.width,
    WASH.height,
    6000,
    pan_offset=WASH_PAN_AIM,
    tilt_offset=WASH_TILT_AIM,
)
BEAM_FAST = Envelope(
    BEAM.algorithms,
    5000,
    BEAM.width,
    BEAM.height,
    6000,
    pan_offset=BEAM_PAN_AIM,
    tilt_offset=BEAM_TILT_AIM,
)

# The rig's 23 EFX all ran Rotation=0 and Parallel propagation, every shape an
# axis-aligned clone of the others (Codex A6). A Serial EFX delays each
# fixture by loopDuration/(fixtureCount+1)*serialNumber (efxfixture.cpp:
# 380-386) for a cascade down the row at no extra cost; Line's smooth cosine
# path (efx.cpp calculatePoint) makes that a wave rather than a stutter.
#
# Diamond and Leaf were wash-only shapes before this task - the beam family
# was deliberately scoped down to Circle/Eight/Line (2026-08-27 review, see
# module docstring). There is no pre-existing beam Diamond or Leaf to rotate,
# so these are new beam figures rather than a rotation on old ones; sharing
# BEAM's duration/width/height keeps them tuned for the same optics.
BEAM_ROTATED_SHAPES = Envelope(
    ("Diamond", "Leaf"),
    BEAM.duration,
    BEAM.width,
    BEAM.height,
    BEAM.hold,
    rotation_by_algorithm={"Diamond": 90, "Leaf": 45},
    pan_offset=BEAM.pan_offset,
    tilt_offset=BEAM.tilt_offset,
)
# Square and Lissajous were wash-only, so their buttons left the four beams
# standing still - "algunos movimientos de cabezas no incluyen las beam" (owner,
# 2026-09-22). Same shapes, the beams' own window and figure time.
BEAM_WIDE_SHAPES = Envelope(
    ("Square", "Lissajous"),
    BEAM.duration,
    BEAM.width,
    BEAM.height,
    BEAM.hold,
    pan_offset=BEAM.pan_offset,
    tilt_offset=BEAM.tilt_offset,
)
WASH_CASCADE = Envelope(
    ("Line",),
    WASH_SLOW.duration,
    WASH_SLOW.width,
    WASH_SLOW.height,
    WASH_SLOW.hold,
    propagation="Serial",
    pan_offset=WASH_SLOW.pan_offset,
    tilt_offset=WASH_SLOW.tilt_offset,
)
BEAM_CASCADE = Envelope(
    BEAM.algorithms[:1],
    BEAM.duration,
    BEAM.width,
    BEAM.height,
    BEAM.hold,
    propagation="Serial",
    rotation=45,
    pan_offset=BEAM.pan_offset,
    tilt_offset=BEAM.tilt_offset,
)

# The classic club wave: tilt only. QLC+'s Line traces x=y - a diagonal, and
# no rotation makes it vertical (efx.cpp calculatePoint / rotateAndScale mix
# both axes through width and height) - so the pan term is killed by Width 0
# and the wave lives on the tilt alone, cascaded Serial down the row. Per
# family, like every other figure: same shape, each family's own size.
WASH_TILT_WAVE = Envelope(
    ("Line",),
    WASH.duration,
    0,
    WASH.height,
    WASH.hold,
    propagation="Serial",
    pan_offset=WASH.pan_offset,
    tilt_offset=WASH.tilt_offset,
)
BEAM_TILT_WAVE = Envelope(
    ("Line",),
    BEAM.duration,
    0,
    BEAM.height,
    BEAM.hold,
    propagation="Serial",
    pan_offset=BEAM.pan_offset,
    tilt_offset=BEAM.tilt_offset,
)

# The hand-built show kept a "(Simultaneo)" twin of every shape - all heads at
# the same phase, the whole rig tracing one figure together - and its rotation
# crossfaded 5 s between blocks (Chaser 23, FadeIn/FadeOut Common 5000). The
# generated show dropped both (old-vs-new audit, 2026-08-28); the twins come
# back as chaser steps per family, same envelope as the phased version.
MOVEMENT_CROSSFADE_MS = 5000

# The synced push: every head at the same phase (spread_phase=False in the
# EFX), so the rig traces one motion together - with the house-right mirror
# kept, the two sides push toward each other and open apart, which is what a
# "push" means on a truss. Slow and wide: the drama is the unison, not speed.
WASH_UNISON = Envelope(
    ("Line",),
    WASH_SLOW.duration,
    WASH_SLOW.width,
    WASH_SLOW.height,
    WASH_SLOW.hold,
    pan_offset=WASH_SLOW.pan_offset,
    tilt_offset=WASH_SLOW.tilt_offset,
)
# Every shape the washes draw, in the beams' own window and figure time. The
# plain buttons reach all seven through three envelopes (BEAM, plus the rotated
# and the wide shapes); the twins need the same seven or they repeat the fault
# the wide shapes fixed - a button that moves the washes and leaves the four
# beams standing ("algunos movimientos de cabeza no incluyen las beam", owner,
# 2026-09-22). The rotations are BEAM_ROTATED_SHAPES': a diamond and a leaf
# read on a beam only turned onto the truss.
BEAM_TWIN_SHAPES = Envelope(
    WASH.algorithms,
    BEAM.duration,
    BEAM.width,
    BEAM.height,
    BEAM.hold,
    rotation_by_algorithm={"Diamond": 90, "Leaf": 45},
    pan_offset=BEAM.pan_offset,
    tilt_offset=BEAM.tilt_offset,
)
# Same figure, alternate heads reversed: the contrast to the unison push. Every
# shape gets the twin, so the tablet offers the same figure both ways round
# instead of only where somebody thought to define it.
WASH_ALTERNATE = Envelope(
    WASH.algorithms,
    WASH.duration,
    WASH.width,
    WASH.height,
    WASH.hold,
    pan_offset=WASH.pan_offset,
    tilt_offset=WASH.tilt_offset,
)
BEAM_ALTERNATE = Envelope(
    BEAM_TWIN_SHAPES.algorithms,
    BEAM_TWIN_SHAPES.duration,
    BEAM_TWIN_SHAPES.width,
    BEAM_TWIN_SHAPES.height,
    BEAM_TWIN_SHAPES.hold,
    rotation_by_algorithm=BEAM_TWIN_SHAPES.rotation_by_algorithm,
    pan_offset=BEAM_TWIN_SHAPES.pan_offset,
    tilt_offset=BEAM_TWIN_SHAPES.tilt_offset,
)
BEAM_UNISON = Envelope(
    ("Line",),
    BEAM.duration,
    BEAM.width,
    BEAM.height,
    BEAM.hold,
    pan_offset=BEAM.pan_offset,
    tilt_offset=BEAM.tilt_offset,
)


@dataclass(frozen=True)
class GeneratedFamilies:
    slow_id: int | None = None
    slow_beam_id: int | None = None
    wash_id: int | None = None
    beam_id: int | None = None
    fast_wash_id: int | None = None
    fast_beam_id: int | None = None
    fan_id: int | None = None
    # The console's names for "everything moves", spanning both families.
    cabezas_id: int | None = None
    rapidos_id: int | None = None
    # One entry per shape for the console's solo frame, and the chasers the
    # speed dial drives.
    efx_ids: list[int] = field(default_factory=list)
    # Exact movement functions the play page may wrap as manual picks.
    play_pick_ids: list[int] = field(default_factory=list)
    dial_ids: list[int] = field(default_factory=list)


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
            names=overrides,
            spread_phase=spread_phase,
            pan_offset=envelope.pan_offset,
            tilt_offset=envelope.tilt_offset,
            vocabulary=vocabulary,
        )

    slow = _family(washes, WASH_SLOW, None, display("prefix_soft"), soft_path, make_chaser=False)
    slow_beam = _family(
        beams, BEAM_SLOW, display("soft_beams"), display("prefix_soft_beam"), soft_path
    )
    ola_suave = _family(
        washes,
        WASH_CASCADE,
        None,
        display("prefix_wave"),
        soft_path,
        make_chaser=False,
        overrides={"Line": display("soft_wave")},
    )
    wash = _family(washes, WASH, None, "Wash", movement_path, make_chaser=False)
    beam = _family(beams, BEAM, None, "Beam", movement_path, make_chaser=False)
    # The old "(Simultaneo)" twins: same shapes, same envelope, every head at
    # phase 0 so the family traces one figure together.
    wash_sim = _family(
        washes,
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
        beams,
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
    # Each head against its neighbour: the same figure with every other fixture
    # running it backwards, which is the "cada cabeza para un lado" the owner
    # missed.
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
        mirrored=every_other(washes),
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
        mirrored=every_other(beams),
    )
    cascada_beams = _family(
        beams,
        BEAM_CASCADE,
        None,
        # No prefix: the envelope's one shape, Circle, is named by the override.
        None,
        movement_path,
        make_chaser=False,
        overrides={"Circle": display("cascade_beams")},
    )
    # The tilt wave and the synced push, per family like every figure.
    ola_wash = _family(
        washes,
        WASH_TILT_WAVE,
        None,
        display("prefix_wave"),
        movement_path,
        make_chaser=False,
        overrides={"Line": display("vertical_wave_washes")},
    )
    ola_beam = _family(
        beams,
        BEAM_TILT_WAVE,
        None,
        display("prefix_wave"),
        movement_path,
        make_chaser=False,
        overrides={"Line": display("vertical_wave_beams")},
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
    )
