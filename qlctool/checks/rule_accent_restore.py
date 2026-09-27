"""A held accent on a wheel channel that nothing puts back afterwards.

Gobo, prism and colour-wheel channels are LTP: the last value written stays
until somebody writes another. A Flash button is a *temporary* writer - press,
accent, release - but release only takes the flash's own writes away; it does
not restore what was there before, because nothing in QLC+ remembers that. If
the state running underneath never drives that wheel, the accent's position
simply stays: the prism that was flashed for one drop is still in the beam an
hour later, and nobody can say which button did it (Codex review, 2026-08-27).

So every wheel channel a Flash scene touches needs an owner underneath: each
room state that lights the fixture must itself drive that channel, so the
moment the flash releases, the state writes the wheel back where it belongs. A
state that keeps the fixture dark is excused - a wheel nobody can see through
a closed dimmer restores nothing but also shows nothing.
"""

from lxml import etree

from ..find_local import find_local
from ..iter_local import iter_local
from ..vc.build_button import NO_FUNCTION
from .finding import WARNING, Finding
from .instant_evaluator import InstantEvaluator
from .orphaned_wheel_writes import orphaned_wheel_writes
from .show_graph import ShowGraph

RULE_ID = "accent_restore"


def check_accent_restore(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], root: etree._Element, states: set[int]
) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None or not states:
        return []
    findings: list[Finding] = []
    # One evaluator for the whole rule: its instant cache is what makes asking
    # the same state about every strobe channel of every flash affordable.
    evaluator = InstantEvaluator(graph, groups)
    for button in iter_local(console, "Button"):
        action = find_local(button, "Action")
        if action is None or (action.text or "").strip() != "Flash":
            continue
        function = find_local(button, "Function")
        if function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        scene = graph.functions.get(function_id)
        if scene is None:
            continue
        caption = button.attrib.get("Caption", "")
        for fixture_name, orphan_states in orphaned_wheel_writes(
            graph, groups, scene, states, evaluator
        ).items():
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=WARNING,
                    function=graph.name(function_id),
                    message_id="accent_restore_wheel_left",
                    fields={"caption": caption, "states": ", ".join(orphan_states)},
                    fixtures=(fixture_name,),
                )
            )
    return findings
