"""Milliseconds one full pass of an RGBMatrix takes on its own group."""

from lxml import etree

from ..find_local import find_local
from ..matrix_step_count import matrix_step_count


def matrix_pass_duration(matrix: etree._Element, grids: dict[int, tuple[int, int]]) -> int:
    speed = find_local(matrix, "Speed")
    group = find_local(matrix, "FixtureGroup")
    if speed is None or group is None or not (group_text := (group.text or "")).isdigit():
        return 0
    algorithm = find_local(matrix, "Algorithm")
    name = None if algorithm is None else (algorithm.text or None)
    width, height = grids.get(int(group_text), (1, 1))
    return int(speed.attrib.get("Duration", 0)) * matrix_step_count(name, width, height)
