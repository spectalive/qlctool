"""Find the held desk accents through their console placement, before replacement."""

from lxml import etree

from .desk_frame_identifiers import desk_frame_identifiers
from .desk_widget import DeskWidget
from .desk_widgets import desk_widgets
from .names.names import Names
from .place import place
from .slugify import slugify
from .split_caption import split_caption


def desk_burst_sources(root: etree._Element, names: Names) -> dict[str, DeskWidget]:
    """Held accents by slug, found through the frames `names` spells.

    `names` is the vocabulary the console was written in: a generator that
    falls back to the default one misses a frame the show renamed and drops
    its bursts without a word (2026-09-25, final review of Plan B).
    """
    widgets = desk_widgets(root)
    frames = {w.id: w for w in widgets if w.kind in ("Frame", "SoloFrame")}
    frame_identifiers = desk_frame_identifiers(frames, names)
    sources = {}
    for widget in widgets:
        if widget.action != "Flash":
            continue
        placement = place(widget, frames, None, names=names, frame_identifiers=frame_identifiers)
        if placement is None or placement.role != "accent":
            continue
        key = slugify(split_caption(widget.caption)[0])
        if key in sources:
            raise ValueError(f"duplicate desk accent: {key}")
        sources[key] = widget
    return sources
