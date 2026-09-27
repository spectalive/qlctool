"""Every Blackout button caption after the first: QLC+ tracks one blackout state.

`vcbutton.cpp:186` handles Blackout without a function signal, while
`VCButtonItem.qml` reads that action's own state for its indicator. Regular
functions can deliberately have several controls; duplicate Blackout
controls instead show conflicting local state.
"""

from lxml import etree

from ..find_local import find_local
from ..xmlutil import localname
from .positioned_widgets import positioned_widgets


def duplicate_blackout_captions(frame: etree._Element) -> list[tuple[str, str]]:
    """(the first Blackout button's caption, each later one's caption)."""
    seen: str | None = None
    found: list[tuple[str, str]] = []
    for widget, _, _ in positioned_widgets(frame):
        if localname(widget) != "Button":
            continue
        action = find_local(widget, "Action")
        if action is None or (action.text or "").strip() != "Blackout":
            continue
        caption = widget.attrib.get("Caption", "")
        if seen is not None:
            found.append((seen, caption))
        else:
            seen = caption
    return found
