"""A flashed strobe that keeps firing after the finger leaves the button.

Strobe channels are LTP: the last value written stays until somebody writes
another. A Flash button writes its strobing value while held and takes only
its own fader away on release - QLC+ restores nothing, because nothing in it
remembers what was there before. If the state running underneath never drives
that strobe channel, the flash's value simply stays: the owner pressed
`FLASH` once and the four panels strobed until somebody found `Strobo OFF`
by hand (owner, 2026-08-28, "se queda el estrobo para siempre").

The wiring that survives this is the one the wash heads already have: every
scene that lights them also parks their shutter channel, so the instant the
flash releases, the running state writes the strobe back off. The rule demands
that shape everywhere: every strobe-capable channel a Flash scene strobes must
be driven by each room state that lights the fixture. A state that keeps the
fixture dark is excused - the latch is invisible until a lit state runs, and
that lit state is the one required to clear it.

A state is read one **instant** at a time (`unowned_while_lit`), not as the
union of everything it reaches. A chaser's steps are alternatives, so a level
that never writes the strobe channel is a latch of its own even when the level
beside it writes strobe-off; merging them would let one level cover for the
next (2026-08-28, from the Codex review of `estrobo pegado`).

Sibling of `rule_accent_restore`, which reads the same LTP latch off the wheel
channels; this one is an error, not a warning, because a strobe nobody can
stop in a dark room full of people is a hazard, not a parked gobo.
"""

from lxml import etree

from ..vc.build_button import NO_FUNCTION
from ..xmlutil import find_local, iter_local
from .finding import ERROR, Finding
from .instant_evaluator import InstantEvaluator
from .latched_strobe_writes import latched_strobe_writes
from .show_graph import ShowGraph

RULE_ID = "strobe_restore"


def check_strobe_restore(
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
        for fixture_name, orphan_states in latched_strobe_writes(
            graph, groups, scene, states, evaluator
        ).items():
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(function_id),
                    message_id="strobe_restore_left_strobing",
                    fields={"caption": caption, "states": ", ".join(orphan_states)},
                    fixtures=(fixture_name,),
                )
            )
    return findings
