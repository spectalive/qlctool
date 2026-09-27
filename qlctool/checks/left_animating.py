"""Whether a colour write leaves a fixture's own animation program running."""

from collections.abc import Mapping

from ..internal_program_of import internal_program
from .color_roles import COLOUR
from .lit import lit
from .show_graph import ShowGraph


def left_animating(graph: ShowGraph, fixture_id: int, written: Mapping[int, int | None]) -> bool:
    capability = graph.capabilities.get(fixture_id)
    if capability is None or capability.is_smoke:
        return False
    program = internal_program(capability)
    if program is None:
        return False

    coloured = {offset for role in COLOUR for offset in capability.offsets_for_role(role)}
    if not any(lit(written[o]) for o in coloured if o in written):
        return False
    return written.get(program.mode_offset) != program.off_value
