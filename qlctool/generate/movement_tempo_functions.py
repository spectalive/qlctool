"""The movement dial's functions: the rotations and their EFX."""

from ..names.names import Names
from ..vc.beat_multiplier import beat_multiplier
from ..vc.dial_function import DialFunction
from ..vc.speed_dial import MULTIPLIER_NONE
from ..workspace import Workspace
from ..xmlutil import find_local, findall_local


def movement_tempo_functions(
    workspace: Workspace, beat_ms: int, vocabulary: Names
) -> list[DialFunction]:
    """(function, multipliers) for the movement dial - rotations and their EFX.

    Both halves, because they are one clock: the chaser says how long a shape
    is shown and the EFX how long its figure takes, and QLC+ subtracts the
    chaser's fade from the EFX's duration to get what it draws
    (`EFX::loopDuration`). Re-time one and not the others and the figure stops
    being a proportion of its step - which is exactly the 6 s sweep of
    2026-08-29. So the fade is re-timed too, as its own multiple of the tap.

    `Movimientos Suaves` is left out: it holds a shape for a minute on
    purpose, which is off this dial's scale and not something anybody taps.
    `vocabulary` spells the rotations' names.
    """
    wanted = tuple(
        vocabulary.display(identifier)
        for identifier in ("wash_movements", "beam_movements", "fast_washes", "fast_beams")
    )
    by_id = {f.attrib.get("ID"): f for f in workspace.engine if f.tag.endswith("}Function")}
    by_name = {f.attrib.get("Name"): f for f in workspace.engine if f.tag.endswith("}Function")}
    functions: dict[int, DialFunction] = {}
    for name in wanted:
        chaser = by_name.get(name)
        if chaser is None:
            continue
        speed = find_local(chaser, "Speed")
        if speed is None:
            continue
        duration = int(speed.attrib.get("Duration", 0))
        fade = int(speed.attrib.get("FadeIn", 0))
        functions[int(chaser.attrib["ID"])] = DialFunction(
            function_id=int(chaser.attrib["ID"]),
            duration=beat_multiplier(duration, beat_ms),
            fade=beat_multiplier(fade, beat_ms) if fade else MULTIPLIER_NONE,
        )
        for step in findall_local(chaser, "Step"):
            shape = by_id.get(step.text)
            if shape is None or shape.attrib.get("Type") != "EFX":
                continue
            shape_speed = find_local(shape, "Speed")
            if shape_speed is None:
                continue
            shape_id = int(shape.attrib["ID"])
            functions[shape_id] = DialFunction(
                function_id=shape_id,
                duration=beat_multiplier(int(shape_speed.attrib.get("Duration", 0)), beat_ms),
            )
    return [functions[key] for key in sorted(functions)]
