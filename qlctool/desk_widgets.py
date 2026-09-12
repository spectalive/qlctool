"""Every Virtual Console widget with the frames above it, flattened for the map.

The console is a tree of frames; the desk wants each widget with its ancestry,
its nearest solo frame, its action and its function, so that a control can be
placed by the frame it sits in and validated against what the master serves
at /vc.json.
"""

from dataclasses import dataclass

from lxml import etree

from .vc.button import NO_FUNCTION
from .xmlutil import find_local, localname

FRAME_TAGS = ("Frame", "SoloFrame")
WIDGET_TAGS = ("Button", "Slider", "SpeedDial", "XYPad", "Label")


@dataclass(frozen=True)
class DeskWidget:
    id: int
    kind: str                  # Frame, SoloFrame, Button, Slider, SpeedDial, XYPad, Label
    caption: str
    page: int
    function: int | None       # a button's function; None for the rest or when unbound
    action: str                # Toggle, Flash, Blackout, StopAll; "" for non-buttons
    key: str | None
    frames: tuple[int, ...]    # ancestor frame ids, outermost first
    solo: int | None           # nearest SoloFrame id
    fade_out_ms: int           # StopAll only
    slider_mode: str           # Slider only: Level, Playback, GrandMaster, ...


def desk_widgets(root: etree._Element) -> list[DeskWidget]:
    """Every frame and widget under the console, in document order."""
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    found: list[DeskWidget] = []
    _walk(console, (), None, 0, found)
    return found


def _walk(parent, frames, solo, page, found) -> None:
    for element in parent:
        tag = localname(element)
        if tag not in FRAME_TAGS and tag not in WIDGET_TAGS:
            continue
        widget_page = int(element.attrib.get("Page", page))
        widget = _widget(element, tag, frames, solo, widget_page)
        found.append(widget)
        if tag in FRAME_TAGS:
            _walk(
                element,
                frames + (widget.id,),
                widget.id if tag == "SoloFrame" else solo,
                widget_page,
                found,
            )


def _widget(element, tag, frames, solo, page) -> DeskWidget:
    function = None
    action = ""
    fade_out = 0
    if tag == "Button":
        bound = find_local(element, "Function")
        if bound is not None:
            function_id = int(bound.attrib.get("ID", NO_FUNCTION))
            function = None if function_id == NO_FUNCTION else function_id
        action_element = find_local(element, "Action")
        action = (action_element.text or "").strip() if action_element is not None else "Toggle"
        action = action or "Toggle"
        if action_element is not None:
            fade_out = int(action_element.attrib.get("FadeOut", 0))
    key_element = find_local(element, "Key")
    key = (key_element.text or "").strip() if key_element is not None else None
    mode_element = find_local(element, "SliderMode") if tag == "Slider" else None
    mode = (mode_element.text or "").strip() if mode_element is not None else ""
    return DeskWidget(
        id=int(element.attrib.get("ID", -1)),
        kind=tag,
        caption=element.attrib.get("Caption", "") or "",
        page=page,
        function=function,
        action=action,
        key=key or None,
        frames=frames,
        solo=solo,
        fade_out_ms=fade_out,
        slider_mode=mode,
    )
