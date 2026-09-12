"""Is there an instant where this fixture is lit and nobody owns this channel?

`reach` merges everything a state can drive through anything it starts, at any
step. That is the right unit for "can these two fight over a channel", and the
wrong unit for "is somebody owning this channel *right now*". A chaser's steps
are alternatives, so a value written by one step is not present while another
plays; union them and one step's owner covers for every other step. That is how
a level of `Ciclo Energia` that never writes a strobe channel hides behind the
level beside it, which does (Codex review of `estrobo pegado`, 2026-08-28).

For the small number of distinct channel values that appear in a fixture's
functions, it is practical to preserve every possible instant. A **Chaser**
picks one step, so its alternatives are unioned. A **Collection** runs all its
members at once, so every combination is considered and simultaneous values
are merged with HTP. This matters for labelled shutters: a pick's numeric
closed value can beat a state's numeric open value even when both roots write
the channel.

**This over-approximates, on purpose.** Treating each member's instants as
independently choosable assumes the concurrent chasers can be caught in every
combination of their steps. Over a night of drifting step lengths they very
nearly can, but two chasers locked to the same clock never would, so a latch
reported here is "reachable unless the timing forbids it" rather than "certain".
That is the right direction to err for a rule about a strobe nobody can stop:
the union it replaces erred the other way and stayed silent. A checker that
modelled the timing would need to model the show, which is the thing it exists
not to have to do.
"""

from .instant_evaluator import InstantEvaluator
from .show_graph import ShowGraph


def unowned_while_lit(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    function_id: int | tuple[int, ...],
    fixture_id: int,
    offsets: frozenset[int],
    dimmers: tuple[int, ...],
    stopped: frozenset[int] = frozenset(),
    evaluator: InstantEvaluator | None = None,
) -> bool:
    """Whether some instant of this function lights the fixture with one of
    `offsets` left to whatever the last writer put there.
    """
    active_evaluator = evaluator or InstantEvaluator(graph, groups)
    return any(
        state.coloured and not state.written
        for offset in offsets
        for state in active_evaluator.states(
            function_id,
            fixture_id,
            offset,
            dimmers,
            stopped,
        )
    )
