"""One speed dial as the desk map describes it."""

from typing import Any

from lxml import etree

from .desk_policy import split_caption
from .desk_widgets import DeskWidget
from .speed_multiplier import multiplier
from .xmlutil import find_local, findall_local


def desk_dial(root: etree._Element, widget: DeskWidget) -> dict[str, Any]:
    element = next(
        (
            e
            for e in root.iter()
            if e.attrib.get("ID") == str(widget.id) and e.tag.endswith("SpeedDial")
        ),
        None,
    )
    members = []
    time_ms = 0
    if element is not None:
        time_element = find_local(element, "Time")
        time_ms = int((time_element.text or "0").strip()) if time_element is not None else 0
        for function in findall_local(element, "Function"):
            members.append(
                {
                    "function": int((function.text or "-1").strip()),
                    "fadeIn": multiplier(int(function.attrib.get("FadeIn", 0))),
                    "fadeOut": multiplier(int(function.attrib.get("FadeOut", 0))),
                    "duration": multiplier(int(function.attrib.get("Duration", 0))),
                }
            )
    return {
        "widget": widget.id,
        "caption": split_caption(widget.caption)[0],
        "key": widget.key,
        "timeMs": time_ms,
        "members": members,
    }
