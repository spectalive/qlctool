"""A strobe left running as one look among many, instead of a button.

This show has a rule it wrote for itself: a strobe is for somebody standing at
the laptop, because a rig strobing unattended all night is not a decision to
make by default. A `Strobe` matrix sitting as one step of a cycle that loops
forever breaks it quietly - the bars simply blink for a couple of seconds every
so often, and what the room reads is not "a strobe", it is "the pixels are off
half the time" (owner, 2026-08-26).

The check is about shape, not names: a strobe that is *a step of a chaser* is a
strobe nobody chose. A strobe on its own button, however it loops internally,
is fine - that is what a strobe button is.
"""

from ..findall_local import findall_local
from .finding import ERROR, Finding
from .is_strobe import is_strobe
from .show_graph import ShowGraph

RULE_ID = "strobe_in_cycle"


def check_strobe_in_cycle(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], entries: dict[int, str]
) -> list[Finding]:
    del groups, entries
    findings: list[Finding] = []
    for function_id, function in sorted(graph.functions.items()):
        if function.attrib.get("Type") != "Chaser":
            continue
        strobes = sorted(
            {
                member.attrib.get("Name", "")
                for step in findall_local(function, "Step")
                if (text := (step.text or "").strip()).isdigit()
                and (member := graph.functions.get(int(text))) is not None
                and is_strobe(member)
            }
        )
        if strobes:
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(function_id),
                    message_id="strobe_in_cycle_steps",
                    fields={"count": len(strobes)},
                )
            )
    return findings
