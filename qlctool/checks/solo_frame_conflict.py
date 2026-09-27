"""Whether another button in the frame would lose its function to this one.

Only scans `solo_frame`'s direct Button children, unlike
`solo_frame_membership`, which follows a SoloFrame's nested plain
Frames too - an asymmetry that is fine today because every SoloFrame this
generator ships holds Buttons directly, never a Button nested inside a
plain Frame of its own; a shipped SoloFrame that grows one would need this
walked the same way.
"""

from lxml import etree

from ..vc.build_button import NO_FUNCTION
from ..xmlutil import find_local, localname


def solo_frame_conflict(target: etree._Element, solo_frame: etree._Element) -> bool:
    for button in solo_frame:
        if localname(button) != "Button" or button is target:
            continue
        function = find_local(button, "Function")
        if function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if function_id != NO_FUNCTION:
            return True
    return False
