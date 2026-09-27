"""The buttons directly inside one SoloFrame, keyed by the function they call."""

from lxml import etree

from ..vc.build_button import NO_FUNCTION
from ..xmlutil import find_local, localname
from .solo_frame_of_or_self import solo_frame_of_or_self


def solo_frame_buttons(frame: etree._Element) -> dict[int, etree._Element]:
    found: dict[int, etree._Element] = {}
    for button in frame.iter():
        if localname(button) != "Button":
            continue
        if solo_frame_of_or_self(button) is not frame:
            continue
        function = find_local(button, "Function")
        if function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if function_id != NO_FUNCTION:
            found[function_id] = button
    return found
