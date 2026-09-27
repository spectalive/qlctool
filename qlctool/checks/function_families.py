"""Family name -> fixtures whose family-defining channels this look writes."""

from .families import FAMILIES
from .reach import reach
from .sets_pixel_mode import sets_pixel_mode
from .show_graph import ShowGraph


def function_families(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> dict[str, set[int]]:
    found: dict[str, set[int]] = {family: set() for family in FAMILIES}
    found["pixel-mode"] = set()
    for fixture_id, written in reach(graph, groups, function_id).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        written_roles = {capability.roles_by_offset[offset] for offset in written}
        for family, family_roles in FAMILIES.items():
            if written_roles & family_roles:
                found[family].add(fixture_id)
        if sets_pixel_mode(capability, written):
            found["pixel-mode"].add(fixture_id)
    return found
