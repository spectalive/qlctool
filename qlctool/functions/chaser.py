"""Build a QLC+ Chaser <Function> element.

A Chaser plays a list of existing functions (usually scenes) in order, each for
its own fade/hold/fade timing. This builder chains scene IDs into steps with a
shared default timing, which is what a colour cycle or a look sequence needs.
"""

from lxml import etree

from ..constants import QLC_NS


def build_chaser(
    function_id: int,
    name: str,
    step_function_ids: list[int],
    fade_in: int = 0,
    hold: int = 1000,
    fade_out: int = 0,
    direction: str = "Forward",
    run_order: str = "Loop",
    path: str | None = None,
) -> etree._Element:
    """Return a `<Function Type="Chaser">` chaining the given function IDs.

    Each step uses the same fade_in/hold/fade_out. direction is Forward/Backward,
    run_order is Loop/SingleShot/PingPong/Random - the values QLC+ accepts.
    """
    function = etree.Element(f"{{{QLC_NS}}}Function")
    function.set("ID", str(function_id))
    function.set("Type", "Chaser")
    function.set("Name", name)
    if path is not None:
        function.set("Path", path)

    speed = etree.SubElement(function, f"{{{QLC_NS}}}Speed")
    speed.set("FadeIn", str(fade_in))
    speed.set("FadeOut", str(fade_out))
    # Chaser Duration is the sum of its steps; QLC+ recomputes it, 0 is fine.
    speed.set("Duration", "0")

    etree.SubElement(function, f"{{{QLC_NS}}}Direction").text = direction
    etree.SubElement(function, f"{{{QLC_NS}}}RunOrder").text = run_order

    modes = etree.SubElement(function, f"{{{QLC_NS}}}SpeedModes")
    modes.set("FadeIn", "Common")
    modes.set("FadeOut", "Common")
    modes.set("Duration", "Common")

    for number, func_id in enumerate(step_function_ids):
        step = etree.SubElement(function, f"{{{QLC_NS}}}Step")
        step.set("Number", str(number))
        step.set("FadeIn", str(fade_in))
        step.set("Hold", str(hold))
        step.set("FadeOut", str(fade_out))
        step.text = str(func_id)

    return function
