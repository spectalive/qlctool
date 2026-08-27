"""Movement per optics family: washes and beams stop sharing one geometry.

All twelve movers ran the same 100x100 EFX at the same speed, which tuned the
show for neither of them - a wash's soft wide beam wants big slow curves, a 7R
needle at that size and speed drags a hard line through faces (Codex review,
2026-08-27). The family split is read off capability: a mover with a gobo
wheel is a beam, one without is a wash - the same line `rule_movement_families`
draws.

Each family gets its own envelope per tempo of the night:

- **Suave** (Ambiente): washes only, two wide slow shapes - the level is calm,
  not parked. The beams hold a static fan instead: a needle's rest is a look.
- **Normal** (Fiesta): both families move, each at its own size and speed, and
  the fan sits in the beams' rotation as a rest step - stillness between
  moving blocks instead of motion as wallpaper.
- **Rapido** (Peak): both families, twice the pace, sized to their optics.

`Movimientos Cabezas` and `Movimientos Rapidos` remain the console's names for
"everything moves": Collections over the family chasers, so the buttons, the
moments and the muscle memory survive the split.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

from .. import roles
from ..capabilities_of import capabilities_of
from ..efx_algorithms import SPANISH_LABELS
from ..functions.chaser import build_chaser
from ..functions.collection import build_collection
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..workspace import Workspace
from .fan_position import generate_fan_position
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


# Sizes and durations are QLC+ raw EFX values, not degrees: a starting
# envelope for on-site tuning, not a universal standard.
WASH_SLOW = Envelope(("Circle", "Line"), 28000, 45, 28, 56000)
WASH = Envelope(
    ("Circle", "Eight", "Line", "Diamond", "Square", "Leaf", "Lissajous"),
    16000, 70, 55, 10000,
)
BEAM = Envelope(("Circle", "Eight", "Line"), 11000, 55, 38, 10000)
WASH_FAST = Envelope(WASH.algorithms, 5000, 80, 50, 6000)
BEAM_FAST = Envelope(BEAM.algorithms, 5000, 70, 40, 6000)

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
    ("Diamond", "Leaf"), BEAM.duration, BEAM.width, BEAM.height, BEAM.hold,
    rotation_by_algorithm={"Diamond": 90, "Leaf": 45},
)
WASH_CASCADE = Envelope(
    ("Line",), WASH_SLOW.duration, WASH_SLOW.width, WASH_SLOW.height,
    WASH_SLOW.hold, propagation="Serial",
)
BEAM_CASCADE = Envelope(
    BEAM.algorithms[:1], BEAM.duration, BEAM.width, BEAM.height, BEAM.hold,
    propagation="Serial", rotation=45,
)


@dataclass(frozen=True)
class GeneratedFamilies:
    slow_id: int | None = None
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
    dial_ids: list[int] = field(default_factory=list)


def generate_movement_families(
    workspace: Workspace,
    library: FixtureLibrary,
    mirrored_ids: Sequence[int] = (),
) -> GeneratedFamilies:
    """Per-family movement, the fan, and the two rig-wide Collections."""
    washes: list[int] = []
    beams: list[int] = []
    for caps in capabilities_of(workspace.root, library):
        if not (caps.has_role(roles.PAN) and caps.has_role(roles.TILT)):
            continue
        family = beams if caps.has_role(roles.GOBO) else washes
        family.append(caps.fixture.fixture_id)
    if not washes and not beams:
        raise ValueError("no fixture in this workspace has both pan and tilt")

    def _family(ids, envelope, name, prefix, path, make_chaser=True, names=None):
        if not ids:
            return None
        return generate_movement_efx(
            workspace, library, algorithms=envelope.algorithms,
            fixture_ids=ids, path=path, make_chaser=make_chaser,
            duration=envelope.duration, width=envelope.width,
            height=envelope.height, chaser_hold=envelope.hold,
            chaser_run_order="Random", chaser_name=name, label_prefix=prefix,
            mirrored_ids=mirrored_ids, propagation_mode=envelope.propagation,
            rotation=envelope.rotation,
            rotation_by_algorithm=envelope.rotation_by_algorithm or None,
            names=names,
        )

    slow = _family(washes, WASH_SLOW, None, "Suave", "Movimiento Suave",
                   make_chaser=False)
    ola_suave = _family(washes, WASH_CASCADE, None, "Ola", "Movimiento Suave",
                        make_chaser=False, names={"Line": "Ola Suave"})
    wash = _family(washes, WASH, "Movimientos Washes", "Wash", "Movimiento")
    beam = _family(beams, BEAM, None, "Beam", "Movimiento", make_chaser=False)
    beam_shapes = _family(beams, BEAM_ROTATED_SHAPES, None, "Beam",
                          "Movimiento", make_chaser=False)
    cascada_beams = _family(beams, BEAM_CASCADE, None, "Cascada", "Movimiento",
                            make_chaser=False, names={"Circle": "Cascada Beams"})
    fast_wash = _family(washes, WASH_FAST, "Rapidos Washes", "Wash Rapido",
                        "Movimiento Rapido")
    fast_beam = _family(beams, BEAM_FAST, "Rapidos Beams", "Beam Rapido",
                        "Movimiento Rapido")

    fan_id = generate_fan_position(workspace, library, beams)

    # The Suave family gets its own cascade wave beside the two plain shapes.
    slow_id: int | None = None
    if slow is not None:
        steps = list(slow.efx_ids) + (
            list(ola_suave.efx_ids) if ola_suave is not None else []
        )
        slow_id = next_function_id(workspace.root)
        workspace.add_function(build_chaser(
            slow_id, "Movimientos Suaves", steps, hold=WASH_SLOW.hold,
            run_order="Random", path="Movimiento Suave",
        ))

    # The beams' rotation carries the fan as a step of its own: a rest the
    # chaser lands on, not a separate button somebody has to remember.
    beam_id: int | None = None
    if beam is not None:
        steps = (
            list(beam.efx_ids)
            + (list(beam_shapes.efx_ids) if beam_shapes is not None else [])
            + (list(cascada_beams.efx_ids) if cascada_beams is not None else [])
            + ([fan_id] if fan_id is not None else [])
        )
        beam_id = next_function_id(workspace.root)
        workspace.add_function(build_chaser(
            beam_id, "Movimientos Beams", steps, hold=BEAM.hold,
            run_order="Random", path="Movimiento",
        ))

    # One entry per shape for the console, whichever families draw it. Diamond
    # and Leaf merge the beam versions into the same button the wash versions
    # already have; Ola Suave and Cascada Beams get a button of their own -
    # their algorithm (Line, Circle) already names an existing button, and
    # merging into it would fire a wash's plain Line whenever the cascade is
    # pressed, or vice versa.
    efx_ids: list[int] = []
    by_shape: dict[str, list[int]] = {}
    for generated, envelope in (
        (wash, WASH), (beam, BEAM), (beam_shapes, BEAM_ROTATED_SHAPES),
    ):
        if generated is None:
            continue
        for shape, efx in zip(envelope.algorithms, generated.efx_ids):
            by_shape.setdefault(shape, []).append(efx)
    for shape in WASH.algorithms:
        members = by_shape.get(shape)
        if not members:
            continue
        collection_id = next_function_id(workspace.root)
        workspace.add_function(build_collection(
            collection_id, f"Movimiento {SPANISH_LABELS.get(shape, shape)}",
            members, path="Movimiento",
        ))
        efx_ids.append(collection_id)
    if ola_suave is not None:
        efx_ids.append(ola_suave.efx_ids[0])
    if cascada_beams is not None:
        efx_ids.append(cascada_beams.efx_ids[0])

    def _both(name, first, second, path):
        members = [m for m in (first, second) if m is not None]
        if not members:
            return None
        collection_id = next_function_id(workspace.root)
        workspace.add_function(
            build_collection(collection_id, name, members, path=path)
        )
        return collection_id

    wash_id = wash.chaser_id if wash is not None else None
    fast_wash_id = fast_wash.chaser_id if fast_wash is not None else None
    fast_beam_id = fast_beam.chaser_id if fast_beam is not None else None
    return GeneratedFamilies(
        slow_id=slow_id,
        wash_id=wash_id,
        beam_id=beam_id,
        fast_wash_id=fast_wash_id,
        fast_beam_id=fast_beam_id,
        fan_id=fan_id,
        cabezas_id=_both("Movimientos Cabezas", wash_id, beam_id, "Movimiento"),
        rapidos_id=_both(
            "Movimientos Rapidos", fast_wash_id, fast_beam_id,
            "Movimiento Rapido",
        ),
        efx_ids=efx_ids,
        dial_ids=[m for m in (wash_id, beam_id) if m is not None],
    )
