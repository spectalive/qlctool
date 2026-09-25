"""A console caption that promises what the rig or the show does not have.

2026-09-25, Plan C final review: the small club's console said "gobos,
prisma y dimmer siguen tu compas" on a rig whose heads have no gobo or prism
wheel, and "los 42 efectos propios de los paneles" with no panel patched.
The generator now chooses those captions from the rig, but `check` said
"ningun problema" either way: no rule read what a caption promises.

The rule reads every `Caption` under the console - frames, solo frames,
labels, buttons and the other widgets - and looks it up in the shipped catalogues:
the identifier whose text, in any shipped language, renders to that caption
(`promise_patterns`; a `{count}` field matches any text). That is a catalogue
lookup, not a guess from a name: no function's name is read. The promises of
the identifier (`CAPTION_PROMISES`) are then asked of the patch
(`promise_kept`), and one finding per caption names each one that is absent.
A caption a show description rewrote through `[names]` is not recoverable
from the workspace, so it is matched only through the shipped catalogues and
an overridden caption is not judged.
"""

from lxml import etree

from ..xmlutil import find_local
from .caption_promises import CAPTION_PROMISES
from .finding import ERROR, Finding
from .promise_kept import promise_kept
from .promise_patterns import promise_patterns
from .promise_words import PROMISE_WORDS
from .show_graph import ShowGraph

RULE_ID = "caption_promise"


def check_caption_promise(graph: ShowGraph, root: etree._Element) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    findings: list[Finding] = []
    for widget in console.iter():
        caption = (widget.get("Caption") or "").strip() if isinstance(widget.tag, str) else ""
        if not caption:
            continue
        identifier = next(
            (key for key, pattern in promise_patterns() if pattern.fullmatch(caption)), None
        )
        if identifier is None:
            continue
        missing = [p for p in CAPTION_PROMISES[identifier] if not promise_kept(p, graph)]
        if not missing:
            continue
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=ERROR,
                function=caption,
                message=(
                    f"el rotulo ({identifier}) promete {', '.join(PROMISE_WORDS[p] for p in missing)}"
                    " y el rig no lo tiene: la consola habla de algo que no hay"
                ),
            )
        )
    return findings
