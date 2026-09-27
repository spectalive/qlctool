"""A wash lit by a scene that never states its zoom.

Until 2026-08-29 nothing in this rig had a zoom channel, so no generator had a
reason to mention one. That night two Mac Mah MAC WASH 1915Z came in place of
the CromoWash100s, and their beam width is DMX: a scene that sets colour and
dimmer and says nothing about zoom leaves the head wherever the last look left
it, which on a cold desk is 0 - whichever end of the zoom that is on the
model, and for a week nobody knew which.

It is the shutter's lesson in a second channel: an unwritten channel is not a
neutral one, and the look that owns the light owns every channel that decides
whether the light is the shape it is meant to be.

The rule: a Scene that lights a fixture - dimmer or colour above zero - must
write that fixture's zoom too, when the definition gives it one that says which
end is wide (`zoom_wide_pairs`). Scenes that only move, only strobe or only
black out are not lighting anything and are left alone.
"""

from .finding import WARNING, Finding
from .lit_without_zoom import lit_without_zoom
from .show_graph import ShowGraph

RULE_ID = "zoom_narrow"


def check_zoom_narrow(graph: ShowGraph, groups: dict[int, tuple[int, ...]]) -> list[Finding]:
    findings: list[Finding] = []
    for function_id in sorted(graph.functions):
        if graph.kind(function_id) != "Scene":
            continue
        silent = lit_without_zoom(graph, groups, function_id)
        if not silent:
            continue
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=WARNING,
                function=graph.name(function_id),
                message_id="zoom_narrow_unwritten",
                fixtures=tuple(sorted(silent)),
            )
        )
    return findings
