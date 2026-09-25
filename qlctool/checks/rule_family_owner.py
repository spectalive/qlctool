"""Keep every playable channel family owned by the room states that use it."""

from lxml import etree

from ..xmlutil import find_local, iter_local
from .family_frames import family_frame_problems
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE_ID = "family_owner"


def check_family_owner(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], root: etree._Element, states: set[int]
) -> list[Finding]:
    """Reject incomplete family frames before their SoloFrame can stop a look."""
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    findings: list[Finding] = []
    for frame in iter_local(console, "SoloFrame"):
        problems = family_frame_problems(graph, groups, states, frame)
        if problems is None:
            continue
        for problem in problems:
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(problem.function_id),
                    message_id=problem.said.message_id,
                    fields=problem.said.fields,
                )
            )
    return findings
