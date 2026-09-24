"""Which console frames become which desk pages, and what each control is.

The tablet does not mirror the Mac's console; it reorganises the same widgets
by what the operator is thinking about. This is the one place that says how:
frames are found by catalogue identifier (`qlctool/locales`), so a frame
caption in any shipped language places the same.

A Flash button is never an enabled desk control: the map replaces held
accents with validated private bursts. Placement retains each source accent
so its caption, section and swatches survive the replacement.
"""

import re
from dataclasses import dataclass

from .desk_frame_identifier import desk_frame_identifier
from .desk_widgets import DeskWidget
from .leading_glyph import leading_glyph
from .names.default_names import default_names
from .names.names import Names

HELD_REASON = "held on the Mac"

BURST_FRAME = "Ráfagas del desk"
# Provisional durations in milliseconds, tunable by the owner after a rig test.
BURST_MS = {
    "hit_flash": 8000,
    "hit_flash_slow": 8000,
    "hit_flash_colour": 8000,
    "hit_strobe": 4000,
    "hit_strobe_soft": 4000,
    "hit_smoke_now": 3000,
    "hit_vertical_smoke_now": 3000,
    "red": 8000,
    "green": 8000,
    "blue": 8000,
    "ultraviolet": 8000,
    "yellow": 8000,
    "cyan": 8000,
    "magenta": 8000,
    "white": 8000,
    "orange": 8000,
    "pink": 8000,
}

PAGES = (
    ("live", "LIVE"),
    ("color", "COLOR"),
    ("pixels", "PIXELES"),
    ("heads", "CABEZAS"),
    ("gobos", "GOBOS"),
    ("prism", "PRISMA"),
    ("control", "CONTROL"),
)
FAMILY_PAGES = {
    "family_colour": "color",
    "family_pixels": "pixels",
    "family_heads": "heads",
    "family_gobos": "gobos",
    "family_prism": "prism",
}
# The order sections take on a page: what the operator reaches for first,
# and the bounded hits last.
SECTION_ORDER = ("state", "hooks", "picks", "haze", "chases", "haze-light", "accents")

# Words the tablet puts under a control where the show's own would mislead
# an operator in the dark: a black look is not a stop, and a haze rhythm
# fires the moment it starts. Keyed by the map key, or by role for a whole
# section. The show's names are never touched.
SAFETY_DETAIL_BY_KEY = {
    "todo-negro": "no es parar",
    "pares": "",
    "humo-vertical": "",
}
# Names the tablet shows instead of the show's where the show's would be
# read as something else: the fog fixture's light is not fog, and a chase
# that alternates halves is one thing, not a name and a footnote.
SAFETY_CAPTION_BY_KEY = {
    "humo-vertical": "Luz del humo vertical",
    "pares": "Pares / impares",
}
SAFETY_DETAIL_BY_ROLE = {
    "haze": "dispara ya",
}
SECTION_TITLES = {
    "state": "LA SALA ESTÁ ASÍ",
    "accents": "GOLPES",
    "haze": "HUMO AMBIENTE",
    "hooks": "AUTO",
    "picks": "ELEGIR",
    "chases": "BARRIDOS DE INTENSIDAD",
    "haze-light": "LUZ DEL HUMO VERTICAL",
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
    names: Names | None = None,
) -> Placement | None:
    """Where a widget goes on the desk, or None when the desk does not show it."""
    vocabulary = default_names() if names is None else names
    if widget.kind != "Button" or widget.function is None:
        return None
    held = widget.action == "Flash"
    if widget.action not in ("Toggle", "Flash"):
        return None
    within = {
        desk_frame_identifier(frames[fid].caption, vocabulary)
        for fid in widget.frames
        if fid in frames
    }
    if "room_states" in within:
        return Placement("live", "state", "state", True, "")
    if "hits" in within:
        if held:
            return Placement("live", "accents", "accent", False, HELD_REASON)
        return Placement("live", "accents", "toggle", True, "")
    if "haze" in within:
        return Placement("live", "haze", "haze", True, "")
    if "colour_hits" in within:
        return Placement("color", "accents", "accent", False, HELD_REASON)
    for family, page in FAMILY_PAGES.items():
        if family in within:
            if held:
                return None
            prefixes = vocabulary.spellings("pick_prefix")
            pick = any((function_name or "").startswith(prefix) for prefix in prefixes)
            return Placement(
                page, "picks" if pick else "hooks", "pick" if pick else "hook", True, ""
            )
    if "intensity_chases" in within:
        # The dimmer chases are what the desk offers here; the fixture strobe
        # toggles beside them are Scenes and wait for a later phase.
        if held or function_kind not in ("Chaser", "Collection", "Sequence"):
            return None
        return Placement("control", "chases", "chase", True, "")
    # The console prefixes each master button with its glyph; the caption this
    # compares against is the one the generator names (2026-09-22).
    if vocabulary.lookup(leading_glyph(widget.caption)[1], ("captions",)) == (
        "vertical_smoke_light",
    ):
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
    if not sep:
        # A two-colour contrast, "Cabezas Rojo / Resto Azul", reads as a
        # name and its second half rather than one long line.
        head, sep, detail = text.partition(" / ")
    return head.strip(), detail.strip() if sep else ""
