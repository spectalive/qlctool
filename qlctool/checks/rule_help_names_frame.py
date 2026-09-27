"""A help line that names a frame its page does not draw.

Round G review, 2026-09-26: page 4's help names the two-colour mixes and the
matrices only where `live_console` draws their frames (`library_help_lines`,
`has_mixes`, `has_matrices`), and the caption-promise rule cannot hold that
choice, because no fixture capability shows either frame - it is a fact about
the console. So a hand-edited console that keeps "the mixes" in its help after
deleting the mixes frame passed `check`.

The rule reads the console itself: for each help line that names a frame, in
any shipped language, a frame with that caption must sit on the same page.
"""

from lxml import etree

from ..names.frame_caption_head import frame_caption_head
from ..xmlutil import find_local, iter_local
from .catalogue_spellings import catalogue_spellings
from .finding import ERROR, Finding
from .help_line import HELP_LINE_FRAMES, MIXES, help_line
from .phrase import Phrase
from .widget_page import widget_page

RULE_ID = "help_names_frame"

# A plain frame or a solo frame: the matrices sit in a SoloFrame, the mixes in a Frame.
FRAME_TAGS = ("Frame", "SoloFrame")


def check_help_names_frame(root: etree._Element) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    frames_by_page: dict[str, set[str]] = {}
    for tag in FRAME_TAGS:
        for frame in iter_local(console, tag):
            head = frame_caption_head(frame.get("Caption", ""))
            frames_by_page.setdefault(widget_page(frame), set()).add(head)
    findings: list[Finding] = []
    for label in iter_local(console, "Label"):
        caption = label.get("Caption", "")
        identifier = help_line(caption)
        if identifier is None:
            continue
        drawn = frames_by_page.get(widget_page(label), set())
        for wanted in HELP_LINE_FRAMES[identifier]:
            heads = {
                frame_caption_head(text)
                for frame_id in wanted
                for text in catalogue_spellings(frame_id)
            }
            if heads & drawn:
                continue
            promised = Phrase("mixes_frame") if wanted == (MIXES,) else Phrase("matrices_frame")
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=caption,
                    message_id="help_names_frame_missing",
                    fields={"frame": promised},
                )
            )
    return findings
