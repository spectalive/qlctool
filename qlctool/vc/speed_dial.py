"""Build a Virtual Console <SpeedDial> that re-times running functions.

The dial writes its value into every function listed under it, scaled by a
multiplier per speed field. Only the Duration multiplier is used here, and only
a chaser whose `SpeedModes Duration` is `Common` answers to it: in `PerStep`,
ChaserRunner::stepDuration reads the step and ignores the chaser, and
Chaser::tap() refuses outright.
"""

from collections.abc import Sequence

from lxml import etree

from ..constants import QLC_NS
from .appearance import build_appearance
from .window_state import build_window_state

# VCSpeedDialFunction::SpeedMultiplier - the dial's value is multiplied by this
# for each speed field. None leaves the field alone, One applies it as is.
MULTIPLIER_NONE = 0
MULTIPLIER_ONE = 6


def build_speed_dial(
    parent: etree._Element,
    widget_id: int,
    caption: str,
    x: int,
    y: int,
    width: int,
    height: int,
    function_ids: Sequence[int],
    time_ms: int,
    tap_key: str | None = None,
    control_bpm: bool = False,
) -> etree._Element:
    dial = etree.SubElement(parent, f"{{{QLC_NS}}}SpeedDial")
    dial.set("Caption", caption)
    dial.set("ID", str(widget_id))

    build_window_state(dial, x, y, width, height)
    build_appearance(dial, frame_style="Sunken")

    absolute = etree.SubElement(dial, f"{{{QLC_NS}}}AbsoluteValue")
    absolute.set("Minimum", "0")
    absolute.set("Maximum", str(max(time_ms * 4, 1000)))

    etree.SubElement(dial, f"{{{QLC_NS}}}Time").text = str(time_ms)
    if control_bpm:
        # The tap sets the workspace's global BPM instead of this widget's
        # time (VCSpeedDial::tap -> InputOutputMap::setBpmNumber). Only a
        # function in Beats tempo hears it - and a dial that controls the BPM
        # should list no functions at all, because tap() still writes the raw
        # tap interval into every listed function's duration on the way.
        etree.SubElement(dial, f"{{{QLC_NS}}}ControlBPM").text = "True"
    if tap_key is not None:
        # A bare <Key> child is not a thing qmlui loads ("Unknown speed dial
        # tag"): the tap is the dial's external control 1, and a key reaches
        # it as an <Input> carrying that ID (VCSpeedDial::loadXML ->
        # loadXMLInputSource; slotInputValueChanged INPUT_TAP_ID -> tap()).
        tap = etree.SubElement(dial, f"{{{QLC_NS}}}Input")
        tap.set("ID", "1")
        tap.set("Key", tap_key)

    for function_id in function_ids:
        function = etree.SubElement(dial, f"{{{QLC_NS}}}Function")
        function.set("FadeIn", str(MULTIPLIER_NONE))
        function.set("FadeOut", str(MULTIPLIER_NONE))
        function.set("Duration", str(MULTIPLIER_ONE))
        function.text = str(function_id)

    return dial
