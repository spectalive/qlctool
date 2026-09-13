"""Find candidate burst controls without trusting their action or function type."""

from lxml import etree

from .desk_policy import BURST_FRAME
from .desk_widgets import DeskWidget, desk_widgets
from .slug import slugify


def desk_burst_buttons(root: etree._Element) -> dict[str, list[DeskWidget]]:
    widgets = desk_widgets(root)
    frames = {
        w.id for w in widgets if w.caption == BURST_FRAME and w.kind in ("Frame", "SoloFrame")
    }
    found: dict[str, list[DeskWidget]] = {}
    for widget in widgets:
        if widget.kind == "Button" and frames.intersection(widget.frames):
            found.setdefault(slugify(widget.caption), []).append(widget)
    return found
