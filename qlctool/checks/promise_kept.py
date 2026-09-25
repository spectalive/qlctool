"""Whether the patch has what one caption promise names."""

from .. import roles
from ..generate.is_pixel_group import is_pixel_group
from ..internal_program import internal_program
from ..is_smoke_machine import is_smoke_machine
from .caption_promises import BEAM_WHEEL, BUILTIN_EFFECTS, HAZE, PIXEL_GROUP
from .show_graph import ShowGraph


def promise_kept(promise: str, graph: ShowGraph, groups: dict[int, tuple[int, ...]]) -> bool:
    """True when some patched fixture, or fixture group, has what `promise` names.

    Capabilities only: a role is a channel some fixture carries; a haze machine
    is `is_smoke_machine`, as the generator's title asks it; a beam wheel is a fixture with
    both a gobo and a colour wheel, the ones the beam wheel frame is built
    from; a pixel group and built-in effects are the generator's own
    predicates, `is_pixel_group` and `internal_program` (smoke machines left
    out, as `generate_builtin_effects` leaves them out).
    """
    caps = list(graph.capabilities.values())
    if promise == HAZE:
        return any(is_smoke_machine(c) for c in caps)
    if promise == BEAM_WHEEL:
        return any(c.has_role(roles.GOBO) and c.has_role(roles.COLOR_MACRO) for c in caps)
    if promise == PIXEL_GROUP:
        return any(is_pixel_group(caps, members) for members in groups.values())
    if promise == BUILTIN_EFFECTS:
        return any(not c.is_smoke and internal_program(c) is not None for c in caps)
    return any(c.has_role(promise) for c in caps)
