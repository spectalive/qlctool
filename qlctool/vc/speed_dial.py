"""Build a Virtual Console <SpeedDial> that re-times running functions.

The dial holds one time and writes it into every function listed under it,
scaled by **that function's own multiplier**: QLC+ computes
`duration = dial time x multiplier` (`VCSpeedDial::applyFunctionsTime`). The
multiplier is what keeps a show sane under one control - the dial's time is a
beat, and each layer states how many beats it takes. A dial that gives every
function the same multiplier flattens a 8-beat colour wheel and a 1-beat
dimmer pulse to the same length, which is what "se vuelven todos los programas
locos" was (owner, 2026-08-29).

Only a chaser whose `SpeedModes Duration` is `Common` answers at all: in
`PerStep`, ChaserRunner::stepDuration reads the step and ignores the chaser,
and Chaser::tap() refuses outright.
"""

from collections.abc import Sequence

from lxml import etree

from ..constants import QLC_NS
from .appearance import build_appearance
from .window_state import build_window_state

# VCSpeedDialFunction::SpeedMultiplier - the dial's value is multiplied by this
# for each speed field. None leaves the field alone; the rest are the fractions
# and multiples QLC+ offers, and nothing between them exists.
MULTIPLIER_NONE = 0
MULTIPLIERS: dict[float, int] = {
    1 / 16: 2, 1 / 8: 3, 1 / 4: 4, 1 / 2: 5,
    1: 6, 2: 7, 4: 8, 8: 9, 16: 10,
}


def build_speed_dial(
    parent: etree._Element,
    widget_id: int,
    caption: str,
    x: int,
    y: int,
    width: int,
    height: int,
    functions: Sequence["DialFunction"],
    time_ms: int,
    tap_key: str | None = None,
    control_bpm: bool = False,
) -> etree._Element:
    """`functions` are `DialFunction`s - a function id and its multipliers.

    `control_bpm` makes the tap set the workspace's global BPM instead
    (`VCSpeedDial::tap` -> `InputOutputMap::setBpmNumber`), which is what a
    show whose layers count in Beats wants. **QLC+ 5.2.2 does not have it** -
    it logs "Unknown speed dial tag: ControlBPM" and ignores the element - so
    it is only for the build meant for a newer QLC+.
    """
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
        etree.SubElement(dial, f"{{{QLC_NS}}}ControlBPM").text = "True"
    if tap_key is not None:
        # A bare <Key> child is not a thing qmlui loads ("Unknown speed dial
        # tag"): the tap is the dial's external control 1, and a key reaches
        # it as an <Input> carrying that ID (VCSpeedDial::loadXML ->
        # loadXMLInputSource; slotInputValueChanged INPUT_TAP_ID -> tap()).
        tap = etree.SubElement(dial, f"{{{QLC_NS}}}Input")
        tap.set("ID", "1")
        tap.set("Key", tap_key)

    for bound in functions:
        function = etree.SubElement(dial, f"{{{QLC_NS}}}Function")
        function.set("FadeIn", str(bound.fade))
        function.set("FadeOut", str(bound.fade))
        function.set("Duration", str(bound.duration))
        function.text = str(bound.function_id)

    return dial
