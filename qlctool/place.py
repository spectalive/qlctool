"""Where a console widget goes on the tablet desk, or None if it does not."""

from .desk_frame_identifier import desk_frame_identifier
from .desk_widgets import DeskWidget
from .leading_glyph import leading_glyph
from .names.default_names import default_names
from .names.names import Names
from .placement import FAMILY_PAGES, HELD_REASON, Placement


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
