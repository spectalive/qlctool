"""Whether the patch has what one caption promise names."""

from .. import roles
from ..generate.fader_dimmed import fader_dimmed
from ..internal_program import internal_program
from ..is_bar import is_bar
from ..is_panel import is_panel
from ..is_smoke_machine import is_smoke_machine
from .caption_promises import BAR, BEAM_WHEEL, BUILTIN_EFFECTS, DIMMER, HAZE, HEADS, PANEL
from .show_graph import ShowGraph


def promise_kept(promise: str, graph: ShowGraph) -> bool:
    """True when some patched fixture has what `promise` names.

    Capabilities only: a role is a channel some fixture carries; a haze machine
    is `is_smoke_machine`, as the generator's title asks it; a beam wheel is a fixture with
    both a gobo and a colour wheel, the ones the beam wheel frame is built
    from; a bar, a panel and built-in effects are the generator's own
    predicates, `is_bar`, `is_panel` and `internal_program` (smoke machines
    left out, as `generate_builtin_effects` leaves them out); a head has pan and
    tilt, as `moving_head_ids` asks; a dimmer is `fader_dimmed`, the dimmer
    chases' own test.
    """
    caps = list(graph.capabilities.values())
    if promise == HAZE:
        return any(is_smoke_machine(c) for c in caps)
    if promise == BEAM_WHEEL:
        return any(c.has_role(roles.GOBO) and c.has_role(roles.COLOR_MACRO) for c in caps)
    if promise == BAR:
        return any(is_bar(c) for c in caps)
    if promise == PANEL:
        return any(is_panel(c) for c in caps)
    if promise == HEADS:
        return any(c.has_role(roles.PAN) and c.has_role(roles.TILT) for c in caps)
    if promise == DIMMER:
        return any(fader_dimmed(c) for c in caps)
    if promise == BUILTIN_EFFECTS:
        return any(not c.is_smoke and internal_program(c) is not None for c in caps)
    return any(c.has_role(promise) for c in caps)
