"""Find candidate burst controls without trusting their action or function type."""

from lxml import etree

from .desk_frame_identifier import desk_frame_identifier
from .desk_widgets import DeskWidget, desk_widgets
from .names.default_names import default_names
from .names.names import Names
from .slug import slugify


def desk_burst_buttons(
    root: etree._Element, names: Names | None = None
) -> dict[str, list[DeskWidget]]:
    vocabulary = default_names() if names is None else names
    widgets = desk_widgets(root)
    frames = {
        w.id
        for w in widgets
        if w.kind in ("Frame", "SoloFrame")
        and desk_frame_identifier(w.caption, vocabulary) == "desk_bursts"
    }
    found: dict[str, list[DeskWidget]] = {}
    for widget in widgets:
        if widget.kind == "Button" and frames.intersection(widget.frames):
            found.setdefault(slugify(widget.caption), []).append(widget)
    return found
