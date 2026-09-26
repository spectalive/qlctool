"""The functions the buttons of one SoloFrame start, and no nested frame's."""

from lxml import etree

from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, localname
from .solo_frame_of import solo_frame_of


def solo_frame_function_ids(frame: etree._Element) -> tuple[int, ...]:
    """Each function a button of `frame` itself starts, once, in console order."""
    found: list[int] = []
    for button in frame.iter():
        if localname(button) != "Button" or solo_frame_of(button) is not frame:
            continue
        function = find_local(button, "Function")
        if function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if function_id != NO_FUNCTION and function_id not in found:
            found.append(function_id)
    return tuple(found)
