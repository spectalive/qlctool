"""Patch the SMC-PAD in as the show's MIDI input, so the pads work on load.

Every `<Input>` binding the console carries was dead in the shipped files: no
universe declared a MIDI input patch, so QLC+ opened the show with nothing
listening and the pad did nothing until somebody walked to the Inputs/Outputs
tab and set it up by hand. At a venue, in the dark, that is a show that does
not start.

Two details make the patch portable rather than a snapshot of one machine, the
same argument `output_binding` makes for the DMX side:

- The line is matched **by name**, not by the line number QLC+ happened to save
  (`InputOutputMap::setInputPatch` tries the UID, then the display name, then
  the stored number). `Line="0"` is only the fallback.
- `midichannel="16"` is omni. The pad speaks on MIDI channel 10 for the pads
  and 1 for the knobs, and a patch pinned to either channel hears half the
  surface; omni is also what makes the channel numbers in `smc_pad_device`
  correct, since QLC+ only ORs the MIDI channel into the channel number in
  omni mode.

The port name is the USB one. Over Bluetooth the pad appears as a different
CoreMIDI source ("SMC-PAD Bluetooth"), so a wireless night needs the input
re-picked in the tab - `docs/show-operation.md` says so.
"""

from lxml import etree

from .constants import QLC_NS
from .generate.input_profile import PROFILE_NAME
from .xmlutil import find_local, iter_local

INPUT_PLUGIN = "MIDI"
# The pad's USB CoreMIDI source, as macOS names it on the show Mac.
INPUT_LINE_NAME = "SINCO SMC-PAD-Master"
FALLBACK_LINE = "0"
OMNI_MIDI_CHANNEL = "16"


def pin_midi_input(root: etree._Element) -> None:
    """Give universe 0 the SMC-PAD input patch, in place."""
    engine = find_local(root, "Engine")
    io_map = find_local(engine, "InputOutputMap") if engine is not None else None
    if io_map is None:
        return
    universe = find_local(io_map, "Universe")
    if universe is None:
        return
    existing = find_local(universe, "Input")
    if existing is not None:
        universe.remove(existing)
    patch = etree.Element(
        f"{{{QLC_NS}}}Input",
        Plugin=INPUT_PLUGIN,
        Name=INPUT_LINE_NAME,
        UID="",
        Line=FALLBACK_LINE,
        Profile=PROFILE_NAME,
    )
    parameters = etree.SubElement(patch, f"{{{QLC_NS}}}PluginParameters")
    parameters.set("midichannel", OMNI_MIDI_CHANNEL)
    # QLC+ writes the input patch first inside <Universe>, ahead of <Output>.
    universe.insert(0, patch)


def midi_input_patch(root: etree._Element) -> etree._Element | None:
    """The universe-0 MIDI input patch, or None if the show has no listener."""
    engine = find_local(root, "Engine")
    io_map = find_local(engine, "InputOutputMap") if engine is not None else None
    if io_map is None:
        return None
    for universe in iter_local(io_map, "Universe"):
        patch = find_local(universe, "Input")
        if patch is not None:
            return patch
    return None
