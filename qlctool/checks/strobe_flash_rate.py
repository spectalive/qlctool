"""What makes a function *a strobe*, read off what it writes - never its name.

A strobe is a shape: something that swings the same intensity channels between
lit and black, fast. Two functions in this show have that shape - a Chaser
alternating a full look with a black one, and an RGBMatrix running the `Strobe`
algorithm, which paints the group full then black on alternate steps. Both
rules that care (the 4 Hz cap and the latched-strobe check, Codex review
2026-08-27) need the same answer: how many times per second does this thing
flash, if it flashes at all.

The rate of a chaser pair is `1000 / (lit hold + black hold)` - one full cycle
is one flash. A matrix's is `1000 / (2 * duration)`, one step lit and one step
black. A step whose duration is zero advances on the engine tick, which QLC+
runs at 20 ms: that is 25 flashes a second, not "no time at all".
"""

from .chaser_flash_rate import chaser_flash_rate
from .matrix_flash_rate import matrix_flash_rate
from .show_graph import ShowGraph


def strobe_flash_rate(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> float | None:
    """Flashes per second this function produces, or None when it is no strobe."""
    function = graph.functions.get(function_id)
    if function is None:
        return None
    kind = function.attrib.get("Type")
    if kind == "RGBMatrix":
        return matrix_flash_rate(function)
    if kind != "Chaser":
        return None
    return chaser_flash_rate(graph, groups, function)
