"""Build a QLC+ Chaser <Function> element.

A Chaser plays a list of existing functions (usually scenes) in order, each for
its own fade/hold/fade timing. This builder chains scene IDs into steps, either
on one shared timing or on a hold per step.
"""

from collections.abc import Sequence

from lxml import etree

from ..constants import QLC_NS


def build_chaser(
    function_id: int,
    name: str,
    step_function_ids: list[int],
    fade_in: int = 0,
    hold: int | Sequence[int] = 1000,
    fade_out: int = 0,
    direction: str = "Forward",
    run_order: str = "Loop",
    path: str | None = None,
) -> etree._Element:
    """Return a `<Function Type="Chaser">` chaining the given function IDs.

    hold is milliseconds, either one value for every step or one per step.
    direction is Forward/Backward, run_order is Loop/SingleShot/PingPong/Random
    - the values QLC+ accepts.
    """
    holds = (
        [int(hold)] * len(step_function_ids)
        if isinstance(hold, int)
        else [int(h) for h in hold]
    )
    if len(holds) != len(step_function_ids):
        raise ValueError(
            f"{len(holds)} holds for {len(step_function_ids)} steps"
        )

    function = etree.Element(f"{{{QLC_NS}}}Function")
    function.set("ID", str(function_id))
    function.set("Type", "Chaser")
    function.set("Name", name)
    if path is not None:
        function.set("Path", path)

    # QLC+ takes a step's duration from the chaser (SpeedModes Duration="Common")
    # or from the step itself ("PerStep") - ChaserRunner::stepDuration. Common is
    # what a Speed Dial and Chaser::tap() drive, and they are ignored in PerStep,
    # so Common is used wherever the steps all last the same. Whichever mode,
    # the duration QLC+ compares against must not be 0: a step whose duration is
    # 0 is over on the engine tick it started, and the chaser walks itself at
    # 50 steps a second.
    uniform = len(set(holds)) == 1
    speed = etree.SubElement(function, f"{{{QLC_NS}}}Speed")
    speed.set("FadeIn", str(fade_in))
    speed.set("FadeOut", str(fade_out))
    speed.set("Duration", str(fade_in + holds[0]))

    etree.SubElement(function, f"{{{QLC_NS}}}Direction").text = direction
    etree.SubElement(function, f"{{{QLC_NS}}}RunOrder").text = run_order

    modes = etree.SubElement(function, f"{{{QLC_NS}}}SpeedModes")
    modes.set("FadeIn", "Common")
    modes.set("FadeOut", "Common")
    modes.set("Duration", "Common" if uniform else "PerStep")

    for number, (func_id, step_hold) in enumerate(zip(step_function_ids, holds)):
        step = etree.SubElement(function, f"{{{QLC_NS}}}Step")
        step.set("Number", str(number))
        step.set("FadeIn", str(fade_in))
        step.set("Hold", str(step_hold))
        step.set("FadeOut", str(fade_out))
        step.text = str(func_id)

    return function
