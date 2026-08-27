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
    """One family's movement at one tempo: shapes, size, and speed."""

    algorithms: tuple[str, ...]
    duration: int
    width: int
    height: int
    hold: int


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

    def _family(ids, envelope, name, prefix, path, make_chaser=True):
        if not ids:
            return None
        return generate_movement_efx(
            workspace, library, algorithms=envelope.algorithms,
            fixture_ids=ids, path=path, make_chaser=make_chaser,
            duration=envelope.duration, width=envelope.width,
            height=envelope.height, chaser_hold=envelope.hold,
            chaser_run_order="Random", chaser_name=name, label_prefix=prefix,
            mirrored_ids=mirrored_ids,
        )

    slow = _family(washes, WASH_SLOW, "Movimientos Suaves", "Suave",
                   "Movimiento Suave")
    wash = _family(washes, WASH, "Movimientos Washes", "Wash", "Movimiento")
    beam = _family(beams, BEAM, None, "Beam", "Movimiento", make_chaser=False)
    fast_wash = _family(washes, WASH_FAST, "Rapidos Washes", "Wash Rapido",
                        "Movimiento Rapido")
    fast_beam = _family(beams, BEAM_FAST, "Rapidos Beams", "Beam Rapido",
                        "Movimiento Rapido")

    fan_id = generate_fan_position(workspace, library, beams)

    # The beams' rotation carries the fan as a step of its own: a rest the
    # chaser lands on, not a separate button somebody has to remember.
    beam_id: int | None = None
    if beam is not None:
        steps = list(beam.efx_ids) + ([fan_id] if fan_id is not None else [])
        beam_id = next_function_id(workspace.root)
        workspace.add_function(build_chaser(
            beam_id, "Movimientos Beams", steps, hold=BEAM.hold,
            run_order="Random", path="Movimiento",
        ))

    # One entry per shape for the console, whichever families draw it.
    efx_ids: list[int] = []
    by_shape: dict[str, list[int]] = {}
    for generated, envelope in ((wash, WASH), (beam, BEAM)):
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
        slow_id=slow.chaser_id if slow is not None else None,
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
