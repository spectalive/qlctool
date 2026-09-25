"""A console frame or solo frame with no control in it.

2026-09-25, Plan C preflight (D9): the first show built for a rig with no haze
machine put `HUMO AMBIENTE — cada cuánto dispara solo` on page 1 as a solo
frame with not one button in it, and the JUGAR page kept its gobo and prism
families - a caption, a line of guidance and an empty picks frame - on a rig
with no gobo wheel and no prism. `qlctool check` said "ningun problema": every
rule asks about the buttons that exist, and none about a frame that has none.

A frame on a console is a promise that something is there to press. One that
holds only labels, or nothing, or only frames that are themselves empty, has
nothing to press. A frame built on purpose as a legend is reported too: the
finding says only that, and `docs/checks.md` records the limit. The rule reads
the widget tree and nothing else: the frame's caption only names it in the
finding. The console's own root frame is the canvas, not a widget, and is not
asked.
"""

from lxml import etree

from ..xmlutil import find_local, localname
from .finding import WARNING, Finding
from .frame_holds_a_control import frame_holds_a_control

RULE_ID = "empty_frame"


def check_empty_frames(root: etree._Element) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    canvas = find_local(console, "Frame") if console is not None else None
    if canvas is None:
        return []
    findings: list[Finding] = []
    for frame in canvas.iter():
        if not isinstance(frame.tag, str) or frame is canvas:
            continue
        if localname(frame) not in ("Frame", "SoloFrame") or frame_holds_a_control(frame):
            continue
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=WARNING,
                function=frame.get("Caption") or f"{localname(frame)} {frame.get('ID')}",
                message_id="empty_frame_nothing_to_press",
            )
        )
    return findings
