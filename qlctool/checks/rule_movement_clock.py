"""Two long movement rotations in one Collection drift onto unrelated shapes."""

from .finding import WARNING, Finding
from .show_graph import ShowGraph

RULE_ID = "movement_clock"


def check_movement_clock(graph: ShowGraph) -> list[Finding]:
    """Find concurrent full-length EFX rotations with independent step clocks."""
    findings: list[Finding] = []
    for function_id in sorted(graph.functions):
        if graph.kind(function_id) != "Collection":
            continue
        rotations = [
            member
            for member in graph.members.get(function_id, ())
            if graph.kind(member) == "Chaser"
            and len(graph.members.get(member, ())) >= 7
            and any(graph.kind(descendant) == "EFX" for descendant in graph.descendants(member))
        ]
        if len(rotations) < 2:
            continue
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=WARNING,
                function=graph.name(function_id),
                message_id="movement_clock_drift",
                fields={"count": len(rotations)},
            )
        )
    return findings
