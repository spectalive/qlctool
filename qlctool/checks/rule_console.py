"""The console's own traps, which a workspace can load cleanly and still have.

Four of them have already cost a show. A **solo frame** stops every other
widget's function the moment one starts, so a master sharing one with its own
members dies the instant it starts them - that is what killed AUTO. A **key**
reaches every widget on every page, so two buttons on one letter fire both. A
widget past the edge of a 1440x900 canvas is a button nobody can press, because
the show laptop cannot scroll to it. And a widget past the edge of its own
*parent frame* - inside the canvas, so `_off_canvas` never sees it - is a
button drawn clipped or spilling onto whatever sits below or beside that frame:
the librería's Matrices frame grew to 34 buttons on a 6-column layout sized
for 30 (Task 5's curated scripts), and its sixth row rendered into the "Ruedas
y ciclos" frame underneath it (2026-08-27).
"""

from lxml import etree

from ..find_local import find_local
from .duplicate_blackout_captions import duplicate_blackout_captions
from .finding import ERROR, Finding
from .off_canvas_widgets import off_canvas_widgets
from .shared_console_keys import shared_console_keys
from .show_graph import ShowGraph
from .solo_frame_clashes import solo_frame_clashes
from .widgets_out_of_frame import widgets_out_of_frame

RULE_ID = "console"


def check_console(graph: ShowGraph, root: etree._Element, canvas: tuple[int, int]) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    frame = find_local(console, "Frame")
    if frame is None:
        return []

    findings: list[Finding] = []
    for function_name, frame_caption, clash in solo_frame_clashes(graph, frame):
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=ERROR,
                function=function_name,
                message_id="console_solo_clash",
                fields={"frame": frame_caption, "clash": clash},
            )
        )
    for key, captions in shared_console_keys(frame):
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=ERROR,
                function=", ".join(captions),
                message_id="console_same_key",
                fields={"key": key},
            )
        )
    for label, right, bottom in off_canvas_widgets(frame, canvas):
        width, height = canvas
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=ERROR,
                function=label,
                message_id="console_off_screen",
                fields={"right": right, "bottom": bottom, "width": width, "height": height},
            )
        )
    for seen, caption in duplicate_blackout_captions(frame):
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=ERROR,
                function=caption,
                message_id="console_two_blackouts",
                fields={"seen": seen, "caption": caption},
            )
        )
    for label, frame_caption, right, bottom, width, height in widgets_out_of_frame(frame):
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=ERROR,
                function=label,
                message_id="console_out_of_frame",
                fields={
                    "frame": frame_caption,
                    "right": right,
                    "bottom": bottom,
                    "width": width,
                    "height": height,
                },
            )
        )
    return findings
