"""A family pick that stops one state hook and leaves the room dark.

A SoloFrame stops its other Toggle functions when a pick starts. That is how a
pick takes colour, movement or a wheel away from a running room state without
stopping the whole state Collection. It also means the stopped hook cannot be
the only function opening a coloured fixture's dimmer or labelled shutter.
"""

from lxml import etree

from ..xmlutil import find_local, iter_local
from .family_frame_picks import family_frame_picks
from .finding import ERROR, Finding
from .instant_dark_fixtures import instant_dark_fixtures
from .instant_evaluator import InstantEvaluator
from .show_graph import ShowGraph

RULE = "pick que apaga"


def check_pick_darkens(
    graph: ShowGraph, groups, root: etree._Element, states: set[int]
) -> list[Finding]:
    """Reject family picks that black out a reachable room-state instant."""
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    evaluator = InstantEvaluator(graph, groups)
    findings: list[Finding] = []
    for frame in iter_local(console, "SoloFrame"):
        for pick_id, stopped in family_frame_picks(graph, groups, states, frame):
            for state_id in sorted(states):
                dark = instant_dark_fixtures(
                    graph,
                    groups,
                    (state_id, pick_id),
                    stopped,
                    check_shutters=True,
                    evaluator=evaluator,
                )
                if not dark:
                    continue
                findings.append(
                    Finding(
                        rule=RULE,
                        severity=ERROR,
                        function=graph.name(state_id),
                        fixtures=tuple(sorted(dark)),
                        message=(
                            f"el pick «{graph.name(pick_id)}» para sus hooks y deja "
                            f"{len(dark)} aparatos coloreados sin dimmer o con el "
                            "obturador cerrado"
                        ),
                    )
                )
    return findings
