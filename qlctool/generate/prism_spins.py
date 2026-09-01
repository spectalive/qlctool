"""The prism in, turning at more than one speed and in more than one direction.

The generated show had exactly one prism look: inserted, forward, slow (25 on
the 7R's 0-127 forward run). That is the safe one and it is the only one the
room ever saw - "le faltaba usar mas los gobos los prismas etc" (owner,
2026-08-30). A prism is a rotation, and a rotation has a speed and a direction:
three positions on the same channel are three different looks out of hardware
that is already in the beam.

The values are read off the definition's own ranges, never typed in: whichever
capability of the rotation channel a preset names is where that look sits, at
the fraction of its run given here. So a fixture whose reverse run is a
different band still turns the right way.
"""

from dataclasses import dataclass

from .. import roles
from ..capabilities_of import capabilities_of
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..workspace import Workspace

# name, rotation preset, how far along that preset's own range to sit. Slow
# forward already belongs to the plain prism scene; these are the other two
# the wheel can do.
SPINS = (
    ("Prisma Giro Rapido", "RotationClockwiseSlowToFast", 0.85),
    ("Prisma Giro Inverso", "RotationCounterClockwiseSlowToFast", 0.5),
)


@dataclass(frozen=True)
class GeneratedPrismSpins:
    scene_ids: list[int]


def generate_prism_spins(
    workspace: Workspace,
    library: FixtureLibrary,
    path: str = "Prisma",
) -> GeneratedPrismSpins:
    """One scene per extra spin, empty when nothing here has a turning prism."""
    beams = [
        capability
        for capability in capabilities_of(workspace.root, library)
        if capability.has_role(roles.PRISM) and capability.has_role(roles.PRISM_ROTATION)
    ]
    if not beams:
        return GeneratedPrismSpins(scene_ids=[])

    scene_ids: list[int] = []
    for name, preset, fraction in SPINS:
        values: dict[int, list[tuple[int, int]]] = {}
        for capability in beams:
            inserted = _preset_value(capability, roles.PRISM, "PrismEffectOn", 0.5)
            spin = _preset_value(capability, roles.PRISM_ROTATION, preset, fraction)
            if inserted is None or spin is None:
                continue
            offset, _ = capability.wheel_for_role(roles.PRISM)
            pairs = [(offset, inserted)]
            pairs += [
                (rotation_offset, spin)
                for rotation_offset in capability.offsets_for_role(roles.PRISM_ROTATION)
            ]
            values[capability.fixture.fixture_id] = pairs
        if not values:
            continue
        function_id = next_function_id(workspace.root)
        workspace.add_function(build_scene(function_id, name, values, path=path))
        scene_ids.append(function_id)
    return GeneratedPrismSpins(scene_ids=scene_ids)


def _preset_value(capability, role: str, preset: str, fraction: float) -> int | None:
    """Where along the range named by `preset` this look sits, or None."""
    for _, ranges in capability.capabilities_for_role(role):
        for item in ranges:
            if (item.preset or "") == preset:
                span = item.maximum - item.minimum
                return item.minimum + round(span * fraction)
    return None
