"""A Chaser's flash rate, from adjacent steps that fight over the same channels."""

from lxml import etree

from ..xmlutil import find_local, findall_local
from .adjacent_step_pairs import adjacent_step_pairs
from .show_graph import ShowGraph
from .step_intensity_shape import step_intensity_shape

# MasterTimer runs at 50 Hz; a zero-duration step flips every other tick.
TICK_FLASH_HZ = 25.0


def chaser_flash_rate(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function: etree._Element
) -> float | None:
    steps = [
        (int(step.text), int(step.attrib.get("FadeIn", "0")) + int(step.attrib.get("Hold", "0")))
        for step in findall_local(function, "Step")
        if step.text and step.text.strip().isdigit()
    ]
    if len(steps) < 2:
        return None

    shapes = [step_intensity_shape(graph, groups, step_id) for step_id, _ in steps]
    run_order_element = find_local(function, "RunOrder")
    run_order = (run_order_element.text or "").strip() if run_order_element is not None else "Loop"

    rate: float | None = None
    for first, second in adjacent_step_pairs(len(steps), run_order):
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
