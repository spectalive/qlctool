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

from .. import roles
from ..xmlutil import find_local, findall_local
from .show_graph import ShowGraph, reach

INTENSITY_ROLES = (
    roles.DIMMER,
    roles.RED,
    roles.GREEN,
    roles.BLUE,
    roles.WHITE,
    roles.AMBER,
    roles.UV,
    roles.CYAN,
    roles.MAGENTA,
    roles.YELLOW,
)
# MasterTimer runs at 50 Hz; a zero-duration step flips every other tick.
TICK_FLASH_HZ = 25.0
STROBE_ALGORITHM = "Strobe"


def strobe_flash_rate(graph: ShowGraph, groups, function_id: int) -> float | None:
    """Flashes per second this function produces, or None when it is no strobe."""
    function = graph.functions.get(function_id)
    if function is None:
        return None
    kind = function.attrib.get("Type")
    if kind == "RGBMatrix":
        return _matrix_rate(function)
    if kind != "Chaser":
        return None
    return _chaser_rate(graph, groups, function)


def _matrix_rate(function) -> float | None:
    algorithm = find_local(function, "Algorithm")
    if algorithm is None or (algorithm.text or "").strip() != STROBE_ALGORITHM:
        return None
    speed = find_local(function, "Speed")
    duration = int(speed.attrib.get("Duration", "0")) if speed is not None else 0
    if duration <= 0:
        return TICK_FLASH_HZ
    return 1000.0 / (2 * duration)


def _chaser_rate(graph: ShowGraph, groups, function) -> float | None:
    steps = [
        (int(step.text), int(step.attrib.get("FadeIn", "0")) + int(step.attrib.get("Hold", "0")))
        for step in findall_local(function, "Step")
        if step.text and step.text.strip().isdigit()
    ]
    if len(steps) < 2:
        return None

    shapes = [_intensity_shape(graph, groups, step_id) for step_id, _ in steps]
    run_order_element = find_local(function, "RunOrder")
    run_order = (run_order_element.text or "").strip() if run_order_element is not None else "Loop"

    rate: float | None = None
    for first, second in _pairs(len(steps), run_order):
        lit, dark = shapes[first], shapes[second]
        if lit is None or dark is None:
            continue
        lit_channels, lit_on = lit
        dark_channels, dark_on = dark
        # A flash is a lit look and a black look fighting over the *same*
        # channels; two looks on different fixtures are a chase, not a strobe.
        if not lit_on or dark_on or not (lit_channels & dark_channels):
            continue
        cycle = steps[first][1] + steps[second][1]
        pair_rate = TICK_FLASH_HZ if cycle <= 0 else 1000.0 / cycle
        rate = pair_rate if rate is None else max(rate, pair_rate)
    return rate


def _pairs(count: int, run_order: str):
    """The (lit, dark) step index pairs that can be adjacent in time."""
    if run_order == "Random":
        # Any step can follow any other.
        return [(a, b) for a in range(count) for b in range(count) if a != b]
    last = count if run_order == "Loop" else count - 1
    pairs = []
    for index in range(last):
        follower = (index + 1) % count
        pairs.append((index, follower))
        pairs.append((follower, index))
    return pairs


def _intensity_shape(graph: ShowGraph, groups, function_id: int) -> tuple[frozenset, bool] | None:
    """(intensity channels this step writes, whether any of them is lit).

    None when the step writes no intensity channel at all - a gobo scene, a
    position - which can be neither the lit nor the black half of a strobe.
    """
    channels: set[tuple[int, int]] = set()
    lit = False
    for fixture_id, written in reach(graph, groups, function_id).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None or capability.is_smoke:
            continue
        wanted = {
            offset for role in INTENSITY_ROLES for offset in capability.offsets_for_role(role)
        }
        for offset, value in written.items():
            if offset not in wanted:
                continue
            channels.add((fixture_id, offset))
            if value is None or value > 0:
                lit = True
    if not channels:
        return None
    return frozenset(channels), lit
