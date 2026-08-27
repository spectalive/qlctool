"""A Flash button whose function QLC+ cannot actually flash.

`Flash` on a Virtual Console button means "run while held, release cleanly" -
but in the engine only a Scene implements it (`Scene::flash`; the `Function`
base just raises a flag nothing reads). Point a Flash button at a Chaser, an
EFX or a Collection and the press half-works: the state machine marks it
active, nothing runs or nothing releases, and the operator learns not to trust
the console. Found while wiring the highlight buttons after the Codex review
of 2026-08-27, before it could ship.

The rule is about the wiring, not the name on the cap: every button whose
`<Action>` is `Flash` must drive a Scene.
"""

from lxml import etree

from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, iter_local
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE = "flash sin escena"
FLASHABLE = ("Scene",)


def check_flash_scene(graph: ShowGraph, root: etree._Element) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    findings: list[Finding] = []
    for button in iter_local(console, "Button"):
        action = find_local(button, "Action")
        if action is None or (action.text or "").strip() != "Flash":
            continue
        function = find_local(button, "Function")
        if function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if function_id == NO_FUNCTION:
            continue
        kind = graph.kind(function_id)
        if kind in FLASHABLE:
            continue
        findings.append(Finding(
            rule=RULE,
            severity=ERROR,
            function=graph.name(function_id),
            message=(
                f"cuelga en modo Flash del boton "
                f"«{button.attrib.get('Caption', '')}», pero es un "
                f"{kind or 'nada'}: QLC+ solo sabe flashear escenas "
                f"(Scene::flash), asi que el boton se queda a medias"
            ),
        ))
    return findings
