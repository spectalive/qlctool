"""Energy levels: the show goes somewhere instead of running flat all night.

Every professional room is built the same way - a handful of looks per energy
level, low to peak, and the night moves between them. The rule that comes with
it is what an unattended show gets wrong: strobes, fast movement, prisms and big
chases are held back for the peak, because a rig that spends everything in the
first minute has nowhere left to grow. This show ran one AUTO collection with
every effect in it, which is a single energy level for six hours.

The structure here keeps the colour bed running underneath and switches only the
layers on top, so a level change never blacks the room out: `AUTO` starts the
rig-wide colour wheel and the haze itself, and steps this cycle beside them. A
level is a Collection, and the cycle is a Chaser over them with a hold per step -
minutes, in real time, never in beats: the beat drives what happens inside a
level, not how long the night takes to build.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

from ..functions.chaser import build_chaser
from ..functions.collection import build_collection
from ..ids import next_function_id
from ..workspace import Workspace

PATH = "Niveles"


@dataclass(frozen=True)
class EnergyLevel:
    """One level: what runs on top of the colour bed, and for how long."""

    name: str
    members: Sequence[int]
    hold: int


@dataclass(frozen=True)
class GeneratedEnergy:
    level_ids: dict[str, int] = field(default_factory=dict)
    cycle_id: int | None = None


def generate_energy_levels(
    workspace: Workspace,
    levels: Sequence[EnergyLevel],
    order: Sequence[str],
    cycle_name: str = "Ciclo Energia",
) -> GeneratedEnergy:
    """A Collection per level and one Chaser walking `order` through them.

    `order` names levels and may repeat one - the night is a wave, not a ramp,
    so coming down through the middle level is a step of its own rather than a
    jump from peak to quiet.
    """
    level_ids: dict[str, int] = {}
    for level in levels:
        if not level.members:
            continue
        function_id = next_function_id(workspace.root)
        workspace.add_function(
            build_collection(
                function_id, level.name, list(level.members), path=PATH
            )
        )
        level_ids[level.name] = function_id

    holds = {level.name: level.hold for level in levels}
    steps = [name for name in order if name in level_ids]
    if not steps:
        return GeneratedEnergy(level_ids=level_ids)

    cycle_id = next_function_id(workspace.root)
    workspace.add_function(
        build_chaser(
            cycle_id,
            cycle_name,
            [level_ids[name] for name in steps],
            hold=[holds[name] for name in steps],
            run_order="Loop",
            path=PATH,
        )
    )
    return GeneratedEnergy(level_ids=level_ids, cycle_id=cycle_id)
