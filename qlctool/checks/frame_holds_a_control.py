"""Whether a console frame has anything in it an operator can work."""

from lxml import etree

from ..xmlutil import localname

# Every widget QLC+ loads into a frame (qmlui/virtualconsole/vcframe.cpp,
# VCFrame::loadWidgetXML) that does something: a label only says something.
# The RGB matrix widget is written as <Matrix> (KXMLQLCVCAnimation in
# qmlui/virtualconsole/vcanimation.h, KXMLQLCVCMatrix in ui/), not <Animation>.
_CONTROL_TAGS = (
    "Button",
    "Slider",
    "Matrix",
    "AudioTriggers",
    "SpeedDial",
    "XYPad",
    "Clock",
    "CueList",
)


def frame_holds_a_control(frame: etree._Element) -> bool:
    """True when a control sits in this frame, directly or in a frame inside it.

    Labels do not count, and neither does a frame that holds no control
    itself: a caption over nothing, or text explaining buttons that are not
    there, gives the operator nothing to press.
    """
    for child in frame:
        # A comment's tag is not a string; its local name is "", which is no
        # control and no frame.
        tag = localname(child)
        if tag in _CONTROL_TAGS:
            return True
        if tag in ("Frame", "SoloFrame") and frame_holds_a_control(child):
            return True
    return False
