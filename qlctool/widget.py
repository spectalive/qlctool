"""Read one Virtual Console element into a DeskWidget."""

from lxml import etree

from .desk_widget import DeskWidget
from .find_local import find_local
from .vc.build_button import NO_FUNCTION


def widget(
    element: etree._Element, tag: str, frames: tuple[int, ...], solo: int | None, page: int
) -> DeskWidget:
    function: int | None = None
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
