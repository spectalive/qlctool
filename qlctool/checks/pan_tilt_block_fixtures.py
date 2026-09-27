"""The fixtures an EFX inside this block drives on pan and tilt."""

from ..xmlutil import find_local, findall_local
from .efx_driven import EFX_PAN_TILT
from .show_graph import ShowGraph


def pan_tilt_block_fixtures(graph: ShowGraph, function_id: int) -> set[int]:
    moved: set[int] = set()
    for member in graph.descendants(function_id):
        function = graph.functions.get(member)
        if function is None or function.attrib.get("Type") != "EFX":
            continue
        for element in findall_local(function, "Fixture"):
            identifier = find_local(element, "ID")
            if (
                identifier is None
                or not (identifier_text := (identifier.text or "").strip()).isdigit()
            ):
                continue
            mode = find_local(element, "Mode")
            mode_value = int(mode.text) if mode is not None and mode.text else EFX_PAN_TILT
            if mode_value != EFX_PAN_TILT:
                continue
            fixture_id = int(identifier_text)
            if fixture_id in graph.capabilities:
                moved.add(fixture_id)
    return moved
