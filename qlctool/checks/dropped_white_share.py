"""The RGB-only fixtures handed the chromatic remainder of a white split.

`rgbw_split` takes a tint's white share out of red, green and blue and hands it
to the White emitter. That is right on a fixture that has one; on a fixture
without, the share has nowhere to go and the tint arrives as its dim, saturated
remainder - `Rig Pastel Rojo` gave twenty-three fixtures (115, 0, 0), `Luz
Charla` a brown (85, 44, 0) (en-sala DMX audit, 2026-09-26).

So the question is asked of values and capabilities only: a fixture with a
White emitter written above zero whose own RGB is not a grey states a
remainder; a fixture with RGB and no White role written that same raw triple
received the remainder, not the colour. Greys (r = g = b) keep every emitter
whole in the split, so they state no remainder.
"""

from collections.abc import Iterable, Mapping

from .. import roles
from .show_graph import ShowGraph
from .written_rgb import written_rgb

Written = Mapping[int, int | None]


def dropped_white_share(graph: ShowGraph, writes: Iterable[Mapping[int, Written]]) -> set[int]:
    """Fixture ids, across `writes` read together, that lost their white share."""
    remainders: set[tuple[int, int, int]] = set()
    plain: list[tuple[int, tuple[int, int, int]]] = []
    for driven in writes:
        for fixture_id, written in driven.items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None:
                continue
            triple = written_rgb(capability, written)
            if triple is None:
                continue
            whites = capability.offsets_for_role(roles.WHITE)
            if not whites:
                plain.append((fixture_id, triple))
                continue
            white = max((v for o in whites if (v := written.get(o)) is not None), default=0)
            if white > 0 and len(set(triple)) > 1:
                remainders.add(triple)
    return {fixture_id for fixture_id, triple in plain if triple in remainders}
