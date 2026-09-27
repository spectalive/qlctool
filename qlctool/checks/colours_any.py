"""Whether what a function states colours any member of a group."""

from .color_roles import COLOUR
from .driven_channels import Driven
from .lit import lit
from .show_graph import ShowGraph


def colours_any(graph: ShowGraph, stated: Driven, members: tuple[int, ...]) -> bool:
    for fixture_id in members:
        capability = graph.capabilities.get(fixture_id)
        written = stated.get(fixture_id)
        if capability is None or not written:
            continue
        offsets = {o for role in COLOUR for o in capability.offsets_for_role(role)}
        if any(lit(written[o]) for o in offsets if o in written):
            return True
    return False
