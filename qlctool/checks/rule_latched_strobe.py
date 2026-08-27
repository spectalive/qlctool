"""A strobe that keeps going after the finger leaves the button.

This show's own rule is that a strobe is punctuation: somebody presses it on
the hit and it ends. A looping flash chaser on a Toggle button breaks that
quietly - the console's `STROBO` was exactly that (Codex review, 2026-08-27):
one press and the rig flashes until somebody remembers what started it, which
in a dark room full of people is a latched hazard, not an effect.

QLC+ cannot make a chaser momentary - `Flash` buttons only really flash Scenes
(`Scene::flash` is the one implementation) - so the correct shape for a strobe
hit is a bounded burst: a SingleShot chaser that plays its pulses and stops on
its own. The rule therefore reads the graph under every button: a function
with a strobe's shape (see `strobe_shape`) that loops is a latched strobe
wherever it hangs, chaser and button alike.
"""

from ..xmlutil import find_local
from .finding import ERROR, Finding
from .show_graph import ShowGraph
from .strobe_shape import strobe_flash_rate

RULE = "estrobo enganchado"
BOUNDED = "SingleShot"


def check_latched_strobe(graph: ShowGraph, groups, entries) -> list[Finding]:
    findings: list[Finding] = []
    reported: set[int] = set()
    for entry_id, caption in sorted(entries.items()):
        for function_id in sorted(graph.descendants(entry_id)):
            if function_id in reported:
                continue
            function = graph.functions.get(function_id)
            if function is None or function.attrib.get("Type") != "Chaser":
                continue
            if strobe_flash_rate(graph, groups, function_id) is None:
                continue
            run_order = find_local(function, "RunOrder")
            if run_order is not None and (run_order.text or "").strip() == BOUNDED:
                continue
            reported.add(function_id)
            findings.append(Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(function_id),
                message=(
                    f"es un estrobo que hace bucle y cuelga del boton "
                    f"«{caption}»: una pulsacion y el rig parpadea hasta que "
                    f"alguien lo apague; una rafaga es un chaser SingleShot "
                    f"que termina solo"
                ),
            ))
    return findings
