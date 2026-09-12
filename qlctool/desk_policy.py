"""Which console frames become which desk pages, and what each control is.

The tablet does not mirror the Mac's console; it reorganises the same widgets
by what the operator is thinking about. This is the one place that says how:
the frames are found by the captions the generators themselves define, so a
renamed frame breaks here, loudly, rather than silently dropping a page.

A Flash button is never a desk control: the desk holds nothing open across a
network. It is carried in the map, disabled with the reason, so the tablet can
show the operator that the Mac has it.
"""

import re
from dataclasses import dataclass

from .desk_widgets import DeskWidget
from .generate.live_console import (
    CHASES_FRAME,
    HITS_FRAME,
    ROOM_FRAME,
    SMOKE_FRAME,
    SMOKE_LIGHT_CAPTION,
)
from .generate.play_page import COLOR_HITS_FRAME, FAMILY_FRAMES, PICK_PREFIX

HELD_REASON = "held on the Mac"

PAGES = (
    ("live", "LIVE"),
    ("color", "COLOR"),
    ("pixels", "PIXELES"),
    ("heads", "CABEZAS"),
    ("gobos", "GOBOS"),
    ("prism", "PRISMA"),
    ("control", "CONTROL"),
)
FAMILY_PAGES = dict(zip(FAMILY_FRAMES, ("color", "pixels", "heads", "gobos", "prism")))
SECTION_TITLES = {
    "state": "LA SALA ESTÁ ASÍ",
    "accents": "GOLPES",
    "haze": "HUMO AMBIENTE",
    "hooks": "AUTO",
    "picks": "ELEGIR",
    "chases": "BARRIDOS",
    "haze-light": "HUMO VERTICAL",
}


@dataclass(frozen=True)
class Placement:
    page: str
    section: str
    role: str
    enabled: bool
    reason: str


def place(
    widget: DeskWidget,
    frames: dict[int, DeskWidget],
    function_name: str | None,
    function_kind: str = "",
) -> Placement | None:
    """Where a widget goes on the desk, or None when the desk does not show it."""
    if widget.kind != "Button" or widget.function is None:
        return None
    held = widget.action == "Flash"
    if widget.action not in ("Toggle", "Flash"):
        return None
    heads = [_head(frames[fid].caption) for fid in widget.frames if fid in frames]
    if _head(ROOM_FRAME) in heads:
        return Placement("live", "state", "state", True, "")
    if _head(HITS_FRAME) in heads:
        if held:
            return Placement("live", "accents", "accent", False, HELD_REASON)
        return Placement("live", "accents", "toggle", True, "")
    if _head(SMOKE_FRAME) in heads:
        return Placement("live", "haze", "haze", True, "")
    if _head(COLOR_HITS_FRAME) in heads:
        return Placement("color", "accents", "accent", False, HELD_REASON)
    for family, page in FAMILY_PAGES.items():
        if family in heads:
            if held:
                return None
            pick = (function_name or "").startswith(PICK_PREFIX)
            return Placement(page, "picks" if pick else "hooks", "pick" if pick else "hook", True, "")
    if _head(CHASES_FRAME) in heads:
        # The dimmer chases are what the desk offers here; the fixture strobe
        # toggles beside them are Scenes and wait for a later phase.
        if held or function_kind not in ("Chaser", "Collection", "Sequence"):
            return None
        return Placement("control", "chases", "chase", True, "")
    if widget.caption == SMOKE_LIGHT_CAPTION:
        return Placement("control", "haze-light", "toggle", True, "")
    return None


def split_caption(caption: str) -> tuple[str, str]:
    """A Mac caption into the desk's two lines: the name and the explanation.

    "AUTO — el show se lleva solo · Q" -> ("AUTO", "el show se lleva solo");
    "AUTO colores · W" -> ("AUTO colores", ""); "Rig Rojo" -> ("Rig Rojo", "").
    The key hint after " · " is the Mac keyboard's business, not the tablet's.
    """
    text = re.sub(r"\s·\s\S+$", "", caption).strip()
    head, sep, detail = text.partition(" — ")
    return head.strip(), detail.strip() if sep else ""


def _head(caption: str) -> str:
    return caption.split(" — ")[0].strip()
