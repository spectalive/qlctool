"""The colour and gobo wheels a definition's ranges describe.

A QLC+ wheel channel lists its slots as capabilities: a `ColorMacro` range with
the colour in `Res1`, a `GoboMacro` range with the image. GDTF keeps the wheel
apart from the channel - a `Wheel` of `Slot`s that the channel's functions then
index - and packs each gobo image into the archive under `wheels/`. A shake
range names the same gobo as the plain one, so slots are keyed by what they
show, not by which range mentions them.
"""

from pathlib import Path

from pygdtf import Wheel, WheelSlot

from .. import roles
from ..definition import FixtureDefinition
from .wheel_name import wheel_name
from .wheel_plan import WheelPlan
from .wheel_slot import wheel_slot

COLOR_SLOT_PRESETS = ("ColorMacro", "ColorDoubleMacro")
GOBO_SLOT_PRESETS = ("GoboMacro", "GoboShakeMacro")


def build_wheels(definition: FixtureDefinition, gobo_dir: Path | None) -> WheelPlan:
    plan = WheelPlan()
    for channel in definition.channels.values():
        if channel.role == roles.COLOR_MACRO:
            presets, prefix = COLOR_SLOT_PRESETS, "Color"
        elif channel.role == roles.GOBO:
            presets, prefix = GOBO_SLOT_PRESETS, "Gobo"
        else:
            continue
        slots: list[WheelSlot] = []
        seen: dict[str, int] = {}
        for index, capability in enumerate(channel.capabilities):
            if capability.preset not in presets:
                continue
            key = capability.resource or capability.name
            if key not in seen:
                slots.append(
                    wheel_slot(prefix, capability.name, capability.resource, gobo_dir, plan)
                )
                seen[key] = len(slots)
            plan.slot_index[(channel.name, index)] = seen[key]
        if not slots:
            continue
        name = f"{prefix}_{wheel_name(channel.name)}"
        plan.wheels.append(Wheel(name=name, wheel_slots=slots))
        plan.by_channel[channel.name] = name
    return plan
