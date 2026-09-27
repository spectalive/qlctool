"""The RGBMatrix steps a chaser cuts off before one full pass finishes."""

from lxml import etree

from ..findall_local import findall_local
from .matrix_pass_duration import matrix_pass_duration
from .show_graph import ShowGraph
from .tempo_element_is_beats import tempo_element_is_beats


def cut_matrix_steps(graph: ShowGraph, chaser: etree._Element) -> list[tuple[str, int, int]]:
    cut: list[tuple[str, int, int]] = []
    for step in findall_local(chaser, "Step"):
        if not (step_text := (step.text or "").strip()).isdigit():
            continue
        matrix = graph.functions.get(int(step_text))
        if matrix is None or matrix.attrib.get("Type") != "RGBMatrix":
            continue
        if tempo_element_is_beats(matrix):
            continue
        needed = matrix_pass_duration(matrix, graph.grids)
        hold = int(step.attrib.get("Hold", 0))
        if needed and hold < needed:
            cut.append((matrix.attrib.get("Name", ""), hold, needed))
    return cut
