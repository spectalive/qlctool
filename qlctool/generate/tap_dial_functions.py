"""The layers the show's tap dial re-times."""

from collections.abc import Mapping, Sequence

from ..names.names import Names
from ..vc.beat_multiplier import beat_multiplier
from ..vc.dial_function import DialFunction
from ..workspace import Workspace
from ..xmlutil import find_local
from .generated_matrices import GeneratedMatrices
from .timed_parts import timed_parts


def tap_dial_functions(
    workspace: Workspace,
    master: Mapping[str, int],
    matrices: Sequence[GeneratedMatrices],
    beat_ms: int,
    vocabulary: Names,
) -> list[DialFunction]:
    """(function id, multiplier) for every layer the tap dial re-times.

    Movement is deliberately absent: a shape takes fifteen seconds and the
    multipliers QLC+ offers stop at sixteen beats, so it cannot be said in
    taps at all - and it carries an EFX clock underneath that a re-timed
    chaser fade would corrupt. `vocabulary` spells the layers' `master` keys.
    """
    wanted = (
        "colour_wheel",
        "simple_wheel",
        "pastel_wheel",
        "multicolour_wheel",
        "mix_wheel",
        "gobo_animation",
        "prism_animation",
        "dimmer_pingpong",
        # The two intensity sweeps. Each is a Collection of one EFX per fixture
        # family, so the dial has to reach the EFX inside: a Collection has no
        # speed of its own and the sweeps kept their own pace whatever the room
        # was doing ("los barridos de intensidad van a su bola", owner,
        # 2026-09-22; `rule_untempoed_rhythm`).
        "dimmer_chase",
        "dimmer_chase_2",
    )
    by_id = {f.attrib.get("ID"): f for f in workspace.engine if f.tag.endswith("}Function")}
    functions: list[DialFunction] = []
    for identifier in wanted:
        function_id = master.get(vocabulary.display(identifier))
        element = by_id.get(str(function_id))
        if element is None:
            continue
        for timed in timed_parts(element, by_id):
            speed = find_local(timed, "Speed")
            if speed is None:
                continue
            functions.append(
                DialFunction(
                    function_id=int(timed.attrib["ID"]),
                    duration=beat_multiplier(int(speed.attrib.get("Duration", 0)), beat_ms),
                )
            )
    return functions
