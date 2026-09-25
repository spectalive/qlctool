"""Whether the patch has what one caption promise names."""

from .. import roles
from ..generate.is_pixel_group import is_pixel_group
from ..internal_program import internal_program
from .caption_promises import BEAM_WHEEL, BUILTIN_EFFECTS, HAZE, PIXEL_GROUP
from .show_graph import ShowGraph


def promise_kept(promise: str, graph: ShowGraph, groups: dict[int, tuple[int, ...]]) -> bool:
    """True when some patched fixture, or fixture group, has what `promise` names.

    Capabilities only: a role is a channel some fixture carries; a haze machine
    is a smoke-typed fixture or one with a pump; a beam wheel is a fixture with
    both a gobo and a colour wheel, the ones the beam wheel frame is built
    from; a pixel group and built-in effects are the generator's own
    predicates, `is_pixel_group` and `internal_program`.
    """
    caps = list(graph.capabilities.values())
    if promise == HAZE:
        return any(c.is_smoke or c.has_role(roles.SMOKE) for c in caps)
    if promise == BEAM_WHEEL:
        return any(c.has_role(roles.GOBO) and c.has_role(roles.COLOR_MACRO) for c in caps)
    if promise == PIXEL_GROUP:
        return any(is_pixel_group(caps, members) for members in groups.values())
    if promise == BUILTIN_EFFECTS:
        return any(internal_program(c) is not None for c in caps)
    return any(c.has_role(promise) for c in caps)
